from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
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
from datetime import datetime, timedelta
import logging

MAX_CAPTION_LENGTH = 1024

RARITY_MAPPING = {
    1: "� Rare",
    2: "🄀 Medium",
    3: "🦄 Legendary",
    4: "🐮 Special Edition",
    5: "🔮 Limited Edition",
    6: "🌐 Celestial",
    7: "🔞 Erotic",
    8: "💕 Valentine Special",
    9: "🎭 X Verse",
    10: "🎃 Halloween Special",
    11: "❄️ Winter Special",
    12: "☄️ Summer Special",
    13: "🎴 AMV",
    14: "🎥 Hollywood"
}

user_favorites = {}

async def get_user_rarity_mode(user_id):
    # Dummy function to simulate rarity filter setting, replace with actual logic
    return "All"

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
    unique_characters = []
    seen_ids = set()
    for character in characters:
        if character['id'] not in seen_ids:
            unique_characters.append(character)
            seen_ids.add(character['id'])

    rarity_mode = await get_user_rarity_mode(user_id)
    if rarity_mode != 'All':
        unique_characters = [char for char in unique_characters if char.get('rarity') == rarity_mode]

    total_pages = max(math.ceil(len(unique_characters) / 15), 1)
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}\n\n"
    current_characters = unique_characters[page*15:(page+1)*15]
    grouped = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, chars in grouped.items():
        harem_message += f"⌜ {anime} 〔{len(chars)}/{len(current_characters)}〕\n"
        for char in chars:
            count = len([c for c in current_characters if c['id'] == char['id']])
            rarity = RARITY_MAPPING.get(char.get('rarity'), 'Unknown')
            harem_message += f"◈⌐{rarity}⌑ {char['id']} {char['name']} ×{count}\n"
        harem_message += "\n"

    harem_message = harem_message[:MAX_CAPTION_LENGTH]

    total_count = len(user['characters'])
    keyboard = [
        [InlineKeyboardButton(f"Collection ({total_count})", callback_data=f"collection:{page}")],
        [InlineKeyboardButton("🎋 AMV & Hollywood", callback_data=f"show:amv_&_hollywood:{page}")],
        [InlineKeyboardButton("Close", callback_data="close")]
    
    reply_markup = InlineKeyboardMarkup(keyboard)

    fav_character_id = user_favorites.get(user_id)
    if fav_character_id:
        fav_character = next((c for c in unique_characters if c['id'] == fav_character_id), None)
        if fav_character and 'img_url' in fav_character:
            await _send_photo_or_text(update, fav_character['img_url'], harem_message, reply_markup)
            return
    await _send_photo_or_text(update, None, harem_message, reply_markup, current_characters)

async def _send_photo_or_text(update, photo_url, caption, reply_markup, characters=None):
    try:
        if photo_url:
            if update.message:
                await update.message.reply_photo(photo=photo_url, caption=caption, reply_markup=reply_markup)
            else:
                await update.callback_query.edit_message_caption(caption=caption, reply_markup=reply_markup)
        elif characters:
            random_character = random.choice(characters)
            if 'img_url' in random_character:
                if update.message:
                    await update.message.reply_photo(photo=random_character['img_url'], caption=caption, reply_markup=reply_markup)
                else:
                    await update.callback_query.edit_message_caption(caption=caption, reply_markup=reply_markup)
        else:
            await _send_text(update, caption, reply_markup)
    except BadRequest:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)

async def _send_text(update, text, reply_markup):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)

async def fav(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if len(context.args) != 1:
        await update.message.reply_text('Usage: /fav <character_id>')
        return

    fav_id = context.args[0]
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text("You don't have any characters in your collection.")
        return

    character = next((c for c in user['characters'] if c['id'] == fav_id), None)
    if not character:
        await update.message.reply_text(f"Character with ID {fav_id} not found in your collection.")
        return

    user_favorites[user_id] = fav_id
    await update.message.reply_text(f"Character with ID {fav_id} has been set as your favorite.")

application.add_handler(CommandHandler("fav", fav))
application.add_handler(CommandHandler("harem", harem))
application.add_handler(CallbackQueryHandler(lambda update, context: update.callback_query.message.delete(), pattern='^close$'))
application.add_handler(CallbackQueryHandler(lambda u, c: harem(u, c, page=int(u.callback_query.data.split(':')[1])), pattern='^collection:'))
application.add_error_handler(lambda update, context: logging.error(f"Error: {context.error}"))
