from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from itertools import groupby
import math
import random
from html import escape
from shivu import user_collection, application
from telegram.error import BadRequest

MAX_CAPTION_LENGTH = 1024

RARITY_MAPPING = {
    '🔱 Rare': '🔱',
    '🌀 Medium': '🌀',
    '🦄 Legendary': '🦄',
    '💮 Special Edition': '💮',
    '🔮 Limited Edition': '🔮',
    '🔞 Erotic': '🔞',
    '🎭 X Verse': '🎭',
    '🎐 Celestial': '🎐',
    '🎃 Halloween Special': '🎃',
    '💞 Valentine Special': '💞',
    '❄️ Winter Special': '❄️',
    '🌤️ Summer Special': '🌤',
    '📽 Hollywood': '📽',
    '🎴 AMV': '🎴',
}

async def get_user_rarity_mode(user_id: int) -> str:
    user = await user_collection.find_one({'id': user_id})
    return user.get('rarity_mode', 'All') if user else 'All'

async def update_user_rarity_mode(user_id: int, rarity_mode: str) -> None:
    await user_collection.update_one({'id': user_id}, {'$set': {'rarity_mode': rarity_mode}}, upsert=True)

async def harem(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user or 'characters' not in user or not user['characters']:
        message = 'You Have Not Guessed Any Characters Yet...'
        if update.message:
            await update.message.reply_text(message)
        else:
            await update.callback_query.edit_message_text(message)
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}

    rarity_mode = await get_user_rarity_mode(user_id)
    if rarity_mode == 'Images':
        characters = [char for char in characters if char.get('rarity') not in ['🎴 AMV', '📽 Hollywood']]
    elif rarity_mode == 'Videos':
        characters = [char for char in characters if char.get('rarity') in ['🎴 AMV', '📽 Hollywood']]

    total_pages = max(1, math.ceil(len(characters) / 15))
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}\n\n"
    current_chars = characters[page*15:(page+1)*15]
    grouped_by_anime = {k: list(v) for k, v in groupby(current_chars, key=lambda x: x['anime'])}

    for anime, chars in grouped_by_anime.items():
        total_count = sum(character_counts[c['id']] for c in chars)
        harem_message += f"⌬ {anime} 〔{total_count}/{total_count}〕\n"
        added_ids = set()
        for c in chars:
            if c['id'] in added_ids:
                continue
            emoji = RARITY_MAPPING.get(c['rarity'], '')
            count = character_counts[c['id']]
            harem_message += f"◈⌠{emoji}⌡ {c['id']} {c['name']} ×{count}\n"
            added_ids.add(c['id'])
        harem_message += "\n"

    if len(harem_message) > MAX_CAPTION_LENGTH:
        harem_message = harem_message[:MAX_CAPTION_LENGTH]

    total_count = len(user['characters'])
    keyboard = [
        [InlineKeyboardButton(f"Collection ({total_count})", callback_data="set_rarity:Images")],
        [InlineKeyboardButton("🎬 AMV & Hollywood", callback_data="set_rarity:Videos")],
    ]

    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"harem:{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"harem:{page+1}"))
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("❌ Close", callback_data="close")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    try:
        fav_id = user.get('favorites', [None])[0]
        fav_character = next((c for c in user['characters'] if c['id'] == fav_id), None)
        media_url = None

        if fav_character:
            media_url = fav_character.get('video_url') or fav_character.get('img_url')
        else:
            random_char = random.choice(characters)
            media_url = random_char.get('video_url') or random_char.get('img_url')

        if media_url:
            if media_url.endswith(('.mp4', '.mov')) or 'video_url' in (fav_character or random_char):
                await _send_video(update, media_url, harem_message, reply_markup)
            else:
                await _send_photo(update, media_url, harem_message, reply_markup)
        else:
            await _send_text(update, harem_message, reply_markup)

    except Exception as e:
        print("Error sending media:", e)
        await _send_text(update, harem_message, reply_markup)

async def _send_video(update, url, caption, markup):
    if update.message:
        await update.message.reply_video(video=url, caption=caption, reply_markup=markup)
    else:
        try:
            await update.callback_query.edit_message_media(
                media=InputMediaVideo(media=url, caption=caption),
                reply_markup=markup
            )
        except BadRequest:
            await update.callback_query.edit_message_reply_markup(reply_markup=markup)

async def _send_photo(update, url, caption, markup):
    if update.message:
        await update.message.reply_photo(photo=url, caption=caption, reply_markup=markup)
    else:
        try:
            await update.callback_query.edit_message_media(
                media=InputMediaPhoto(media=url, caption=caption),
                reply_markup=markup
            )
        except BadRequest:
            await update.callback_query.edit_message_reply_markup(reply_markup=markup)

async def _send_text(update, text, markup):
    if update.message:
        await update.message.reply_text(text, reply_markup=markup)
    else:
        try:
            await update.callback_query.edit_message_text(text=text, reply_markup=markup)
        except BadRequest:
            await update.callback_query.edit_message_reply_markup(reply_markup=markup)

async def pagination_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    if data.startswith("harem:"):
        page = int(data.split(":")[1])
        await harem(update, context, page)

async def rarity_filter_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id
    mode = query.data.split(":")[1]
    await update_user_rarity_mode(user_id, mode)
    await harem(update, context)

application.add_handler(CommandHandler("harem", harem))
application.add_handler(CallbackQueryHandler(pagination_callback, pattern="^harem:"))
application.add_handler(CallbackQueryHandler(rarity_filter_callback, pattern="^set_rarity:"))
application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.message.delete(), pattern="^close$"))
