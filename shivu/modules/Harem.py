from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from itertools import groupby
import math
import random
from html import escape
from shivu import collection, user_collection, application
from shivu import PARTNER
from shivu import shivuu as app
from pyrogram import filters
from datetime import datetime, timedelta
import logging

MAX_CAPTION_LENGTH = 1024

# Define rarity mapping with updated values
RARITY_MAPPING = {
    1: "🔱 Rare",
    2: "🌀 Medium",
    3: "🦄 Legendary",
    4: "💮 Special Edition",
    5: "🔮 Limited Edition",
    6: "🎐 Celestial",
    7: "🔞 Erotic",
    8: "💞 Valentine Special",
    9: "🎭 X Verse",
    10: "🎃 Halloween Special",
    11: "❄️ Winter Special",
    12: "🌤️ Summer Special",
    13: "🎴 AMV",
    14: "🎥 Hollywood"
}

async def harem(update: Update, context: CallbackContext, page=0) -> None:
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user:
        message = 'You Have Not Guessed any Characters Yet..'
        if update.message:
            await update.message.reply_text(message)
        else:
            await update.callback_query.edit_message_text(message)
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
    rarity_mode = await get_user_rarity_mode(user_id)

    if rarity_mode != 'All':
        characters = [char for char in characters if char.get('rarity') == rarity_mode]

    total_pages = math.ceil(len(characters) / 15)
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}\n\n"
    current_characters = characters[page*15:(page+1)*15]
    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, characters in current_grouped_characters.items():
        harem_message += f"⌬ {anime} 〔{len(characters)}/{character_counts[characters[0]['id']]}〕\n"
        for character in characters:
            count = character_counts[character['id']]
            rarity = character['rarity']
            rarity_emoji = RARITY_MAPPING.get(rarity, 'Unknown')
            harem_message += f"◈⌠{rarity_emoji}⌡ {character['id']} {character['name']} ×{count}\n"
        harem_message += "\n"

    if len(harem_message) > MAX_CAPTION_LENGTH:
        harem_message = harem_message[:MAX_CAPTION_LENGTH]

    total_count = len(user['characters'])
    keyboard = [
        [InlineKeyboardButton(f"See Collection ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}")],
        [InlineKeyboardButton("Waifus", callback_data=f"filter:waifus:{page}"),
         InlineKeyboardButton("AMV & Hollywood", callback_data=f"filter:amv_hollywood:{page}")]
    ]

    if total_pages > 1:
        nav_buttons = []
        if page > 0:
            nav_buttons.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"harem:{page-1}"))
        if page < total_pages - 1:
            nav_buttons.append(InlineKeyboardButton("Next ➡️", callback_data=f"harem:{page+1}"))
        keyboard.append(nav_buttons)

    # Add a close button
    keyboard.append([InlineKeyboardButton("Close", callback_data="close")])

    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(harem_message, reply_markup=reply_markup)

async def filter_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    filter_type, page = data.split(':')[1], int(data.split(':')[2])
    user_id = update.effective_user.id

    user = await user_collection.find_one({'id': user_id})
    characters = user['characters']

    if filter_type == 'waifus':
        characters = [char for char in characters if char['rarity'] not in ['AMV', 'Hollywood']]
    elif filter_type == 'amv_hollywood':
        characters = [char for char in characters if char['rarity'] in ['AMV', 'Hollywood']]

    # Update message with filtered characters
    await harem(update, context, page)

async def get_user_rarity_mode(user_id: int) -> str:
    user = await user_collection.find_one({'id': user_id})
    return user.get('rarity_mode', 'All') if user else 'All'

async def update_user_rarity_mode(user_id: int, rarity_mode: str) -> None:
    await user_collection.update_one({'id': user_id}, {'$set': {'rarity_mode': rarity_mode}}, upsert=True)

def error(update: Update, context: CallbackContext):
    logging.error(f"Error: {context.error}")

async def pagination_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    data = query.data
    page = int(data.split(':')[1])
    await harem(update, context, page)

application.add_handler(CommandHandler(["harem"], harem))
application.add_handler(CallbackQueryHandler(pagination_callback, pattern='^harem:'))
application.add_handler(CallbackQueryHandler(filter_callback, pattern='^filter:'))
application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.message.delete(), pattern='^close$'))
application.add_error_handler(error)
