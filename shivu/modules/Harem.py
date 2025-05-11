from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.error import BadRequest
from itertools import groupby
import math
import random
from html import escape
from shivu import collection, user_collection, application
from shivu import PARTNER
from shivu import shivuu as app
from pyrogram import filters
from datetime import datetime
import logging

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
    '🌤️ Summer Special': '🌤️',
    '📽 Hollywood': '📽',
    '🎴 AMV': '🎴',
}

async def harem(update: Update, context: CallbackContext, page=0):
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user or not user.get('characters'):
        msg = 'You have not guessed any characters yet.'
        if update.message:
            await update.message.reply_text(msg)
        else:
            await update.callback_query.edit_message_text(msg)
        return

    # Group characters by ID, counting them
    character_map = {}
    for char in user['characters']:
        cid = char['id']
        if cid in character_map:
            character_map[cid]['count'] += 1
        else:
            character_map[cid] = char.copy()
            character_map[cid]['count'] = 1

    characters = list(character_map.values())
    characters.sort(key=lambda x: (x['anime'], x['id']))

    total_pages = math.ceil(len(characters) / 15)
    page = max(0, min(page, total_pages - 1))

    grouped_by_anime = {}
    for char in characters[page*15:(page+1)*15]:
        grouped_by_anime.setdefault(char['anime'], []).append(char)

    harem_msg = f"{escape(update.effective_user.first_name)}'s Harem - Page {page + 1}/{total_pages}\n\n"
    for anime, chars in grouped_by_anime.items():
        total = sum(c['count'] for c in chars)
        harem_msg += f"\u231e {anime} 〔{total}/{total}〕\n"
        for c in chars:
            emoji = RARITY_MAPPING.get(c['rarity'], '?')
            harem_msg += f"◈⌠{emoji}⌡ {c['id']} {c['name']} ×{c['count']}\n"
        harem_msg += "\n"

    if len(harem_msg) > MAX_CAPTION_LENGTH:
        harem_msg = harem_msg[:MAX_CAPTION_LENGTH]

    total_count = len(user['characters'])
    keyboard = [
        [InlineKeyboardButton(f"Collection ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}"),
         InlineKeyboardButton("🎋 AMV & Hollywood", switch_inline_query_current_chat=f"collection.{user_id}.AMV")],
    ]

    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"harem:{page - 1}"))
    if page < total_pages - 1:
        nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"harem:{page + 1}"))
    if nav_buttons:
        keyboard.append(nav_buttons)

    keyboard.append([InlineKeyboardButton("Close", callback_data="close")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Choose display image
    preview = next((c for c in characters if 'img_url' in c), None)
    image_url = preview['img_url'] if preview else None

    if update.message:
        if image_url:
            await update.message.reply_photo(image_url, caption=harem_msg, reply_markup=reply_markup)
        else:
            await update.message.reply_text(harem_msg, reply_markup=reply_markup)
    else:
        try:
            if image_url:
                await update.callback_query.edit_message_media(InputMediaPhoto(media=image_url, caption=harem_msg), reply_markup=reply_markup)
            else:
                await update.callback_query.edit_message_caption(caption=harem_msg, reply_markup=reply_markup)
        except BadRequest:
            await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)

async def inline_query_handler(update: Update, context: CallbackContext):
    query = update.inline_query.query
    user_id = None
    mode = 'image'

    if query.startswith("collection."):
        parts = query.split('.')
        try:
            user_id = int(parts[1])
            if len(parts) > 2 and parts[2] == 'AMV':
                mode = 'video'
        except:
            return

    user = await user_collection.find_one({'id': user_id})
    if not user or not user.get('characters'):
        await update.inline_query.answer([], is_personal=True, cache_time=1)
        return

    results = []
    seen_ids = set()
    for idx, char in enumerate(user['characters']):
        if char['id'] in seen_ids:
            continue
        seen_ids.add(char['id'])

        is_amv = char['rarity'] in ['🎴 AMV', '📽 Hollywood']
        if mode == 'image' and is_amv:
            continue
        if mode == 'video' and not is_amv:
            continue

        title = f"{char['name']} - {char['rarity']}"
        if mode == 'video':
            result = telegram.InlineQueryResultVideo(
                id=str(idx),
                video_url=char['img_url'],
                mime_type="video/mp4",
                thumb_url=char['img_url'],
                title=title
            )
        else:
            result = telegram.InlineQueryResultPhoto(
                id=str(idx),
                photo_url=char['img_url'],
                thumb_url=char['img_url'],
                title=title,
                description=char['anime']
            )
        results.append(result)
        if len(results) >= 50:
            break

    await update.inline_query.answer(results, is_personal=True, cache_time=1)

def error_handler(update: Update, context: CallbackContext):
    logging.error(f"Error: {context.error}")

async def pagination_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    page = int(data.split(':')[1])
    await harem(update, context, page)

application.add_handler(CommandHandler("harem", harem))
application.add_handler(CallbackQueryHandler(pagination_callback, pattern='^harem:'))
application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.message.delete(), pattern='^close$'))
application.add_handler(telegram.ext.InlineQueryHandler(inline_query_handler))
application.add_error_handler(error_handler)
