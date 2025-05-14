import re
import time
from html import escape
from cachetools import TTLCache
from pymongo import MongoClient, ASCENDING

from telegram import Update, InlineQueryResultPhoto
from telegram.ext import InlineQueryHandler, CallbackContext, CommandHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from shivu import user_collection, collection, db
from shivu import application

# Ensure indexes for performance
db.characters.create_index([('id', ASCENDING)])
db.characters.create_index([('anime', ASCENDING)])
db.characters.create_index([('img_url', ASCENDING)])

db.user_collection.create_index([('characters.id', ASCENDING)])
db.user_collection.create_index([('characters.name', ASCENDING)])
db.user_collection.create_index([('characters.img_url', ASCENDING)])

# Caching
all_characters_cache = TTLCache(maxsize=10000, ttl=36000)
user_collection_cache = TTLCache(maxsize=10000, ttl=60)

async def inlinequery(update: Update, context: CallbackContext) -> None:
    query = update.inline_query.query
    offset = int(update.inline_query.offset) if update.inline_query.offset else 0

    all_characters = []

    # Handle user collection search
    if query.startswith('collection.'):
        user_id = query.split(' ')[0].split('.')[1]
        search_terms = ' '.join(query.split(' ')[1:])

        if user_id.isdigit():
            user_id_int = int(user_id)
            user = user_collection_cache.get(user_id_int)
            if not user:
                user = await user_collection.find_one({'id': user_id_int})
                if user:
                    user_collection_cache[user_id_int] = user

            if user:
                all_characters = list({v['id']: v for v in user['characters']}.values())

                if search_terms:
                    regex = re.compile(search_terms, re.IGNORECASE)
                    all_characters = [
                        c for c in all_characters
                        if regex.search(c['name']) or regex.search(c['anime'])
                    ]
        else:
            all_characters = []
    else:
        if query:
            regex = re.compile(query, re.IGNORECASE)
            all_characters = await collection.find({
                "$or": [{"name": regex}, {"anime": regex}]
            }).to_list(length=None)
        else:
            if 'all_characters' in all_characters_cache:
                all_characters = all_characters_cache['all_characters']
            else:
                all_characters = await collection.find({}).to_list(length=None)
                all_characters_cache['all_characters'] = all_characters

    # Paginate
    characters = all_characters[offset:offset+25]
    next_offset = str(offset + len(characters)) if len(all_characters) > offset + 25 else ""

    # Prepare results
    results = []
    for character in characters:
        if 'img_url' not in character:
            continue  # Skip if image URL is missing

        global_count = await user_collection.count_documents({'characters.id': character['id']})
        anime_characters = await collection.count_documents({'anime': character['anime']})
        rarity_text = character.get('rarity', '❔ Unknown')
        rarity_emoji = rarity_text.split()[0]

        if query.startswith('collection.') and user:
            user_character_count = sum(c['id'] == character['id'] for c in user['characters'])
            user_anime_characters = sum(c['anime'] == character['anime'] for c in user['characters'])

            caption = (
                f"<b>Look At <a href='tg://user?id={user['id']}'>"
                f"{escape(user.get('first_name', str(user['id'])))}</a>'s Character</b>\n\n"
                f"🌸: <b>{character['name']} (x{user_character_count})</b>\n"
                f"🏖️: <b>{character['anime']} ({user_anime_characters}/{anime_characters})</b>\n"
                f"{rarity_emoji} <b>{rarity_text}</b>\n\n"
                f"🆔️: <code>{character['id']}</code>"
            )
        else:
            caption = (
                f"<b>Look At This Character !!</b>\n\n"
                f"🌸: <b>{character['name']}</b>\n"
                f"🏖️: <b>{character['anime']}</b>\n"
                f"{rarity_emoji} <b>{rarity_text}</b>\n"
                f"🆔️: <code>{character['id']}</code>\n\n"
                f"<b>Globally Guessed {global_count} Times...</b>"
            )

        results.append(
            InlineQueryResultPhoto(
                thumbnail_url=character['img_url'],
                id=f"{character['id']}_{time.time()}",
                photo_url=character['img_url'],
                caption=caption,
                parse_mode='HTML'
            )
        )

    await update.inline_query.answer(results, next_offset=next_offset, cache_time=5)

# Handler
application.add_handler(InlineQueryHandler(inlinequery, block=False))
