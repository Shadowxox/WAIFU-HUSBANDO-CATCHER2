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

# RARITY_MAPPING with updated values
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

# Global dictionary to store favorites
user_favorites = {}

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

    # Remove repeated characters with the same ID (only show once)
    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    unique_characters = []
    seen_ids = set()
    for character in characters:
        if character['id'] not in seen_ids:
            unique_characters.append(character)
            seen_ids.add(character['id'])

    # Handle rarity filter
    rarity_mode = await get_user_rarity_mode(user_id)
    if rarity_mode != 'All':
        unique_characters = [char for char in unique_characters if char.get('rarity') == rarity_mode]

    total_pages = math.ceil(len(unique_characters) / 15)
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}\n\n"
    current_characters = unique_characters[page*15:(page+1)*15]
    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, characters in current_grouped_characters.items():
        harem_message += f"⌬ {anime} 〔{len(characters)}/{len(current_characters)}〕\n"
        for character in characters:
            count = len([c for c in current_characters if c['id'] == character['id']])
            rarity = character['rarity']
            rarity_emoji = RARITY_MAPPING.get(rarity, 'Unknown')
            harem_message += f"◈⌠{rarity_emoji}⌡ {character['id']} {character['name']} ×{count}\n"
        harem_message += "\n"

    if len(harem_message) > MAX_CAPTION_LENGTH:
        harem_message = harem_message[:MAX_CAPTION_LENGTH]

    total_count = len(user['characters'])
    keyboard = [
        [InlineKeyboardButton(f"See Collection ({total_count})", callback_data=f"see_collection:{page}")],
         InlineKeyboardButton("AMV & Hollywood", callback_data=f"filter:amv_hollywood:{page}")
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

# RARITY_MAPPING with updated values
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

# Global dictionary to store favorites
user_favorites = {}

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

    # Remove repeated characters with the same ID (only show once)
    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    unique_characters = []
    seen_ids = set()
    for character in characters:
        if character['id'] not in seen_ids:
            unique_characters.append(character)
            seen_ids.add(character['id'])

    # Handle rarity filter
    rarity_mode = await get_user_rarity_mode(user_id)
    if rarity_mode != 'All':
        unique_characters = [char for char in unique_characters if char.get('rarity') == rarity_mode]

    total_pages = math.ceil(len(unique_characters) / 15)
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}\n\n"
    current_characters = unique_characters[page*15:(page+1)*15]
    current_grouped_characters = {k: list(v) for k, v in groupby(current_characters, key=lambda x: x['anime'])}

    for anime, characters in current_grouped_characters.items():
        harem_message += f"⌬ {anime} 〔{len(characters)}/{len(current_characters)}〕\n"
        for character in characters:
            count = len([c for c in current_characters if c['id'] == character['id']])
            rarity = character['rarity']
            rarity_emoji = RARITY_MAPPING.get(rarity, 'Unknown')
            harem_message += f"◈⌠{rarity_emoji}⌡ {character['id']} {character['name']} ×{count}\n"
        harem_message += "\n"

    if len(harem_message) > MAX_CAPTION_LENGTH:
        harem_message = harem_message[:MAX_CAPTION_LENGTH]

    total_count = len(user['characters'])
    keyboard = [
        [InlineKeyboardButton(f"Collection ({total_count})", callback_data=f"collection:{page}")],
        [InlineKeyboardButton("🎋 AMV & Hollywood", callback_data=f"show:amv_&_hollywood:{page}")]
    ]

    # Add a close button
    keyboard.append([InlineKeyboardButton("Close", callback_data="close")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get the user's favorite character if set
    fav_character_id = user_favorites.get(user_id)
    if fav_character_id:
        fav_character = next((c for c in unique_characters if c['id'] == fav_character_id), None)
        if fav_character and 'img_url' in fav_character:
            if update.message:
                await update.message.reply_photo(photo=fav_character['img_url'], caption=harem_message, reply_markup=reply_markup)
            else:
                try:
                    await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup)
                except BadRequest:
                    await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
        else:
            await _send_harem_message(update, harem_message, reply_markup)
    else:
        await _send_harem_message(update, harem_message, reply_markup)


async def _send_harem_message(update, harem_message, reply_markup, characters=None):
    if characters:
        random_character = random.choice(characters)
        if 'img_url' in random_character:
            if update.message:
                await update.message.reply_photo(photo=random_character['img_url'], caption=harem_message, reply_markup=reply_markup)
            else:
                try:
                    await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup)
                except BadRequest:
                    await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
        else:
            await _send_text_message(update, harem_message, reply_markup)
    else:
        await _send_text_message(update, harem_message, reply_markup)


async def _send_text_message(update, text, reply_markup):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        try:
            await update.callback_query.edit_message_caption(caption=text, reply_markup=reply_markup)
        except BadRequest:
            await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)


async def fav(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if len(context.args) != 1:
        await update.message.reply_text('Usage: /fav <character_id>')
        return

    fav_id = context.args[0]
    # Check if the character ID exists in the user's collection
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You don\'t have any characters in your collection.')
        return

    # Set the favorite character
    character = next((c for c in user['characters'] if c['id'] == fav_id), None)
    if not character:
        await update.message.reply_text(f"Character with ID {fav_id} not found in your collection.")
        return

    # Store the favorite
    user_favorites[user_id] = fav_id
    await update.message.reply_text(f"Character with ID {fav_id} has been set as your favorite.")

# Add the command handler for /fav
application.add_handler(CommandHandler("fav", fav))

# Add the command handler for /harem
application.add_handler(CommandHandler(["harem"], harem))

# Add the callback query handler for pagination and other actions
application.add_handler(CallbackQueryHandler(lambda update, context: update.callback_query.message.delete(), pattern='^close$'))
application.add_handler(CallbackQueryHandler(lambda u, c: harem(u, c, page=int(u.callback_query.data.split(':')[1])), pattern='^harem:'))
application.add_error_handler(lambda update, context: logging.error(f"Error: {context.error}"))
],
        [InlineKeyboardButton("AMV & Hollywood Videos", callback_data=f"show:amv_hollywood:{page}")]
    ]

    # Add a close button
    keyboard.append([InlineKeyboardButton("Close", callback_data="close")])

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Get the user's favorite character if set
    fav_character_id = user_favorites.get(user_id)
    if fav_character_id:
        fav_character = next((c for c in unique_characters if c['id'] == fav_character_id), None)
        if fav_character and 'img_url' in fav_character:
            if update.message:
                await update.message.reply_photo(photo=fav_character['img_url'], caption=harem_message, reply_markup=reply_markup)
            else:
                try:
                    await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup)
                except BadRequest:
                    await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
        else:
            await _send_harem_message(update, harem_message, reply_markup)
    else:
        await _send_harem_message(update, harem_message, reply_markup)


async def _send_harem_message(update, harem_message, reply_markup, characters=None):
    if characters:
        random_character = random.choice(characters)
        if 'img_url' in random_character:
            if update.message:
                await update.message.reply_photo(photo=random_character['img_url'], caption=harem_message, reply_markup=reply_markup)
            else:
                try:
                    await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup)
                except BadRequest:
                    await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
        else:
            await _send_text_message(update, harem_message, reply_markup)
    else:
        await _send_text_message(update, harem_message, reply_markup)


async def _send_text_message(update, text, reply_markup):
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup)
    else:
        try:
            await update.callback_query.edit_message_caption(caption=text, reply_markup=reply_markup)
        except BadRequest:
            await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)


async def fav(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    if len(context.args) != 1:
        await update.message.reply_text('Usage: /fav <character_id>')
        return

    fav_id = context.args[0]
    # Check if the character ID exists in the user's collection
    user = await user_collection.find_one({'id': user_id})
    if not user:
        await update.message.reply_text('You don\'t have any characters in your collection.')
        return

    # Set the favorite character
    character = next((c for c in user['characters'] if c['id'] == fav_id), None)
    if not character:
        await update.message.reply_text(f"Character with ID {fav_id} not found in your collection.")
        return

    # Store the favorite
    user_favorites[user_id] = fav_id
    await update.message.reply_text(f"Character with ID {fav_id} has been set as your favorite.")

# Add the command handler for /fav
application.add_handler(CommandHandler("fav", fav))

# Add the command handler for /harem
application.add_handler(CommandHandler(["harem"], harem))

# Add the callback query handler for pagination and other actions
application.add_handler(CallbackQueryHandler(lambda update, context: update.callback_query.message.delete(), pattern='^close$'))
application.add_handler(CallbackQueryHandler(lambda u, c: harem(u, c, page=int(u.callback_query.data.split(':')[1])), pattern='^harem:'))
application.add_error_handler(lambda update, context: logging.error(f"Error: {context.error}"))
