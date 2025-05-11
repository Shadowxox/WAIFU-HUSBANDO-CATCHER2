from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto, InputMediaVideo, InlineQueryResultPhoto,
    InlineQueryResultVideo
)
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.ext import Application, InlineQueryHandler
from itertools import groupby
import math
import random
from html import escape
from datetime import datetime
import logging

from shivu import collection, user_collection, application

MAX_CAPTION_LENGTH = 1024

RARITY_MAPPING = {
    '🔱 Rare': '🔱', '🌀 Medium': '🌀', '🦄 Legendary': '🦄',
    '💮 Special Edition': '💮', '🔮 Limited Edition': '🔮',
    '🔞 Erotic': '🔞', '🎭 X Verse': '🎭', '🎐 Celestial': '🎐',
    '🎃 Halloween Special': '🎃', '💞 Valentine Special': '💞',
    '❄️ Winter Special': '❄️', '🌤️ Summer Special': '🌤',
    '📽 Hollywood': '📽', '🎴 AMV': '🎴',
}

async def get_user_rarity_mode(user_id: int) -> str:
    user = await user_collection.find_one({'id': user_id})
    return user.get('rarity_mode', 'All') if user else 'All'

async def update_user_rarity_mode(user_id: int, rarity_mode: str) -> None:
    await user_collection.update_one({'id': user_id}, {'$set': {'rarity_mode': rarity_mode}}, upsert=True)

async def harem(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user:
        message = 'You have not guessed any characters yet.'
        if update.message:
            await update.message.reply_text(message)
        else:
            await update.callback_query.edit_message_text(message)
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {}
    unique_characters = []
    seen_ids = set()
    for char in characters:
        char_id = char['id']
        character_counts[char_id] = character_counts.get(char_id, 0) + 1
        if char_id not in seen_ids:
            unique_characters.append(char)
            seen_ids.add(char_id)

    rarity_mode = await get_user_rarity_mode(user_id)
    if rarity_mode != 'All':
        unique_characters = [char for char in unique_characters if char.get('rarity') == rarity_mode]

    total_pages = max(1, math.ceil(len(unique_characters) / 15))
    page = max(0, min(page, total_pages - 1))

    harem_message += f"◈⌠{rarity_emoji}⌡ {c['id']} {c['name']} ×{character_counts[c['id']]}\n"
    page_chars = unique_characters[page*15:(page+1)*15]
    current_grouped = {k: list(v) for k, v in groupby(page_chars, key=lambda x: x['anime'])}

    for anime, chars in current_grouped.items():
        count = sum(character_counts[c['id']] for c in chars)
        harem_message += f"⌬ {anime} 〔{count}/{count}〕\n"
        for c in chars:
            rarity = c.get('rarity', 'Unknown')
            emoji = RARITY_MAPPING.get(rarity, '❔')
            harem_message += f"◈⌠{emoji}⌡ {c['id']} {c['name']} [{rarity}] ×{character_counts[c['id']]}\n"
        harem_message += "\n"

    harem_message = harem_message[:MAX_CAPTION_LENGTH]
    total_count = len(user['characters'])

    keyboard = [
        [InlineKeyboardButton(f"Collection ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}")],
        [InlineKeyboardButton("🎋 AMV & Hollywood", switch_inline_query_current_chat=f"collection.{user_id}.AMV")]
    ]
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"harem:{page-1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"harem:{page+1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)
    keyboard.append([InlineKeyboardButton("Close", callback_data="close")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    photo_url = None
    fav_id = user.get('favorites', [None])[0]
    if fav_id:
        fav = next((c for c in user['characters'] if c['id'] == fav_id), None)
        if fav and 'img_url' in fav:
            photo_url = fav['img_url']
    if not photo_url and user['characters']:
        random_char = random.choice(user['characters'])
        photo_url = random_char.get('img_url')

    try:
        if update.message:
            await update.message.reply_photo(photo=photo_url, caption=harem_message, reply_markup=reply_markup)
        else:
            try:
                await update.callback_query.edit_message_media(
                    media=InputMediaPhoto(media=photo_url, caption=harem_message),
                    reply_markup=reply_markup
                )
            except:
                await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup)
    except Exception as e:
        print("Error:", e)

async def pagination_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    page = int(query.data.split(':')[1])
    await harem(update, context, page)

async def inline_query_handler(update: Update, context: CallbackContext):
    query = update.inline_query.query
    if not query.startswith('collection.'):
        return

    parts = query.split('.')
    user_id = int(parts[1])
    filter_amv = len(parts) > 2 and parts[2] == 'AMV'

    user = await user_collection.find_one({'id': user_id})
    if not user or 'characters' not in user:
        return

    seen_ids = set()
    results = []
    for char in user['characters']:
        char_id = char['id']
        if char_id in seen_ids:
            continue
        seen_ids.add(char_id)

        name = char['name']
        rarity = char.get('rarity', '')
        if filter_amv and rarity not in ['AMV', 'Hollywood']:
            continue
        if not filter_amv and rarity in ['AMV', 'Hollywood']:
            continue

        media_url = char.get('video_url') if rarity in ['AMV', 'Hollywood'] else char.get('img_url')
        if not media_url:
            continue

        if rarity in ['AMV', 'Hollywood']:
            results.append(
                InlineQueryResultVideo(
                    id=str(char_id),
                    video_url=media_url,
                    mime_type="video/mp4",
                    thumb_url=char.get('thumb_url', media_url),
                    title=f"{name} [{rarity}]",
                    caption=f"{name} [{rarity}]",
                )
            )
        else:
            results.append(
                InlineQueryResultPhoto(
                    id=str(char_id),
                    photo_url=media_url,
                    thumb_url=media_url,
                    title=f"{name} [{rarity}]",
                    caption=f"{name} [{rarity}]",
                )
            )

    await update.inline_query.answer(results[:50], cache_time=1)

def error_handler(update: Update, context: CallbackContext):
    logging.error(f"Update {update} caused error {context.error}")

# Register handlers
application.add_handler(CommandHandler(["harem", "collection"], harem))
application.add_handler(CallbackQueryHandler(pagination_callback, pattern="^harem:"))
application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.message.delete(), pattern="^close$"))
application.add_handler(InlineQueryHandler(inline_query_handler))
application.add_error_handler(error_handler)
