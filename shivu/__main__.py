import datetime
import importlib
import time
import random
import re
import asyncio
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CommandHandler, CallbackContext, MessageHandler, filters
from shivu import (
    app, collection, top_global_groups_collection,
    group_user_totals_collection, user_collection,
    user_totals_collection, shivuu, application, SUPPORT_CHAT,
    UPDATE_CHAT, db, LOGGER
)
from shivu.modules import ALL_MODULES

locks = {}
message_counters = {}
spam_counters = {}
last_characters = {}
sent_characters = {}
first_correct_guesses = {}
message_counts = {}
last_user = {}
warned_users = {}

SPECIAL_SPAWN_GROUP_ID = -1002643948280

for module_name in ALL_MODULES:
    importlib.import_module("shivu.modules." + module_name)

def escape_markdown(text):
    escape_chars = r'\\*_`~>#+-=|{}.!'
    return re.sub(r'([%s])' % re.escape(escape_chars), r'\\\1', text)

async def message_counter(update: Update, context: CallbackContext) -> None:
    chat_id = str(update.effective_chat.id)
    user_id = update.effective_user.id

    if chat_id not in locks:
        locks[chat_id] = asyncio.Lock()
    lock = locks[chat_id]

    async with lock:
        chat_frequency = await user_totals_collection.find_one({'chat_id': chat_id})
        message_frequency = chat_frequency.get('message_frequency', 100) if chat_frequency else 100

        if chat_id in last_user and last_user[chat_id]['user_id'] == user_id:
            last_user[chat_id]['count'] += 1
            if last_user[chat_id]['count'] >= 10:
                if user_id in warned_users and time.time() - warned_users[user_id] < 600:
                    return
                else:
                    return
        else:
            last_user[chat_id] = {'user_id': user_id, 'count': 1}

        message_counts[chat_id] = message_counts.get(chat_id, 0) + 1

        if message_counts[chat_id] % message_frequency == 0:
            await send_image(update, context)
            message_counts[chat_id] = 0

async def send_image(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    all_characters = list(await collection.find({}).to_list(length=None))

    if chat_id not in sent_characters:
        sent_characters[chat_id] = []

    if len(sent_characters[chat_id]) == len(all_characters):
        sent_characters[chat_id] = []

    today_message_count = message_counts.get(chat_id, 0)

    spawn_counts = {
        '🔱 Rare': 15, '🌀 Medium': 6, '🦄 Legendary': 9, '💮 Special Edition': 4,
        '🔮 Limited Edition': 4, '🎐 Celestial': 1, '🎭 X Verse': 1, '🎃 Halloween Special': 0,
        '💞 Valentine Special': 0, '❄️ Winter Special': 1, '🌤️ Summer Special': 1,
        '🔞 Erotic': 0, '🎴 AMV': 0, '🎥 Hollywood': 0
    }

    if chat_id == SPECIAL_SPAWN_GROUP_ID:
        if today_message_count >= 150:
            spawn_counts['🔞 Erotic'] = 1
        if today_message_count >= 300:
            spawn_counts['🎴 AMV'] = 1
        if today_message_count >= 350:
            spawn_counts['🎥 Hollywood'] = 1

    characters_to_spawn = []
    for rarity, count in spawn_counts.items():
        characters_to_spawn.extend([
            c for c in all_characters
            if c.get('id') not in sent_characters[chat_id] and c.get('rarity') == rarity
        ] * count)

    if not characters_to_spawn:
        characters_to_spawn = all_characters

    character = random.choice(characters_to_spawn)
    sent_characters[chat_id].append(character.get('id'))
    last_characters[chat_id] = character

    if chat_id in first_correct_guesses:
        del first_correct_guesses[chat_id]

    caption = f"🌟 A new {character.get('rarity')} character has emerged! Quickly, head to /guess [Name] to reveal its name! 🌟"

    if character.get('img_url'):
        await context.bot.send_photo(chat_id=chat_id, photo=character['img_url'], caption=caption, parse_mode='Markdown')
    elif character.get('vid_url'):
        await context.bot.send_video(chat_id=chat_id, video=character['vid_url'], caption=caption, parse_mode='Markdown')

async def guess(update: Update, context: CallbackContext) -> None:
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id

    if chat_id not in last_characters:
        await update.message.reply_text("No character to guess at the moment. Please wait for one to spawn!")
        return

    if chat_id in first_correct_guesses:
        return

    guess = ' '.join(context.args).lower() if context.args else ''
    if "()" in guess or "&" in guess.lower():
        await update.message.reply_text("Nahh, you can't use those types of words in your guess..❌️")
        return

    name_parts = last_characters[chat_id]['name'].lower().split()
    if sorted(name_parts) == sorted(guess.split()) or any(part == guess for part in name_parts):
        first_correct_guesses[chat_id] = user_id
        character = last_characters[chat_id]
        keyboard = [[InlineKeyboardButton(f"See Harem", switch_inline_query_current_chat=f"collection.{user_id}")]]
        await update.message.reply_text(
            f'<b><a href="tg://user?id={user_id}">{escape(update.effective_user.first_name)}</a></b> 🎊 You guessed the character!\n\n'
            f'🍁 Name: <b>{character["name"]}</b>\n'
            f'⛩ Anime: <b>{character["anime"]}</b>\n'
            f'🎐 Rarity: <b>{character["rarity"]}</b>\n\n'
            f'This character is now in your harem! Use /harem to see your harem.',
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

        user = await user_collection.find_one({'id': user_id})
        if user:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != user.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != user.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await user_collection.update_one({'id': user_id}, {'$set': update_fields})
            await user_collection.update_one({'id': user_id}, {'$push': {'characters': character}})
        else:
            await user_collection.insert_one({
                'id': user_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'characters': [character],
            })

        group_user_total = await group_user_totals_collection.find_one({'user_id': user_id, 'group_id': chat_id})
        if group_user_total:
            update_fields = {}
            if hasattr(update.effective_user, 'username') and update.effective_user.username != group_user_total.get('username'):
                update_fields['username'] = update.effective_user.username
            if update.effective_user.first_name != group_user_total.get('first_name'):
                update_fields['first_name'] = update.effective_user.first_name
            if update_fields:
                await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$set': update_fields})
            await group_user_totals_collection.update_one({'user_id': user_id, 'group_id': chat_id}, {'$inc': {'count': 1}})
        else:
            await group_user_totals_collection.insert_one({
                'user_id': user_id,
                'group_id': chat_id,
                'username': update.effective_user.username,
                'first_name': update.effective_user.first_name,
                'count': 1,
            })

        group_info = await top_global_groups_collection.find_one({'group_id': chat_id})
        if group_info:
            update_fields = {}
            if update.effective_chat.title != group_info.get('group_name'):
                update_fields['group_name'] = update.effective_chat.title
            if update_fields:
                await top_global_groups_collection.update_one({'group_id': chat_id}, {'$set': update_fields})
            await top_global_groups_collection.update_one({'group_id': chat_id}, {'$inc': {'count': 1}})
        else:
            await top_global_groups_collection.insert_one({
                'group_id': chat_id,
                'group_name': update.effective_chat.title,
                'count': 1,
            })
    else:
        await update.message.reply_text('Oᴏᴘs! Cʜᴀᴍᴘ Yᴏᴜ Gᴜᴇssᴇᴅ Tʜᴇ Wʀᴏɴɢ Cʜᴀʀᴀᴄᴛᴇʀ Nᴀᴍᴇ... ❌️')

def error_handler(update: Update, context: CallbackContext):
    LOGGER.error("An error occurred: %s", context.error)

def main() -> None:
    application.add_handler(CommandHandler("guess", guess, block=False))
    application.add_handler(MessageHandler(filters.ALL, message_counter, block=False))
    application.add_error_handler(error_handler)
    asyncio.create_task(application.run_polling(drop_pending_updates=True))

if __name__ == "__main__":
    shivuu.start()
    app.start()
    LOGGER.info("Bot started")
    main()
