import math
from html import escape
from itertools import groupby
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, InputMediaVideo
from telegram.constants import ParseMode
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from telegram.error import BadRequest
from shivu import application, user_collection

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

# Helper: is video?
def is_video(c):
    url = c.get("img_url", "")
    return c.get("rarity") in ['📽 Hollywood', '🎴 AMV'] and url.lower().endswith(('.mp4', '.mov', '.mkv', '.webm'))

# Get User Preference
async def get_user_rarity_mode(user_id: int) -> str:
    user = await user_collection.find_one({'id': user_id})
    return user.get('rarity_mode', 'All') if user else 'All'

# Update User Preference
async def update_user_rarity_mode(user_id: int, rarity_mode: str) -> None:
    await user_collection.update_one({'id': user_id}, {'$set': {'rarity_mode': rarity_mode}}, upsert=True)

# Main /harem Handler
async def harem(update: Update, context: CallbackContext, page=0):
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user or 'characters' not in user or not user['characters']:
        await (update.message or update.callback_query).reply_text('You have not guessed any characters yet.')
        return

    characters = sorted(user['characters'], key=lambda x: (x['anime'], x['id']))
    character_counts = {k: len(list(v)) for k, v in groupby(characters, key=lambda x: x['id'])}
    rarity_mode = await get_user_rarity_mode(user_id)

    # Filter characters
    if rarity_mode == 'AMV':
        characters = [c for c in characters if c.get('rarity') in ['📽 Hollywood', '🎴 AMV']]
    else:
        characters = [c for c in characters if c.get('rarity') not in ['📽 Hollywood', '🎴 AMV']]

    total_pages = max(math.ceil(len(characters) / 15), 1)
    if page < 0 or page >= total_pages:
        page = 0

    harem_message = f"{escape(update.effective_user.first_name)}'s Harem - Page {page+1}/{total_pages}\n\n"
    current_chars = characters[page * 15:(page + 1) * 15]
    grouped = {k: list(v) for k, v in groupby(current_chars, key=lambda x: x['anime'])}

    for anime, chars in grouped.items():
        count = sum(character_counts[char['id']] for char in chars)
        harem_message += f"\u231c {anime} 〔{count}/{count}〕\n"
        used_ids = set()
        for char in chars:
            if char['id'] not in used_ids:
                used_ids.add(char['id'])
                rarity = char['rarity']
                emoji = RARITY_MAPPING.get(rarity, '?')
                harem_message += f"\u25C8\u2310{emoji}\u2321 {char['id']} {char['name']} ×{character_counts[char['id']]}\n"
        harem_message += "\n"

    if len(harem_message) > MAX_CAPTION_LENGTH:
        harem_message = harem_message[:MAX_CAPTION_LENGTH]

    total_count = len(user['characters'])
    keyboard = [
        [
            InlineKeyboardButton(f"Collection ({total_count})", switch_inline_query_current_chat=f"collection.{user_id}"),
            InlineKeyboardButton("🎋 AMV & Hollywood", switch_inline_query_current_chat=f"collection.{user_id}.AMV")
        ]
    ]

    if total_pages > 1:
        nav = []
        if page > 0:
            nav.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"harem:{page-1}"))
        if page < total_pages - 1:
            nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"harem:{page+1}"))
        keyboard.append(nav)

    keyboard.append([InlineKeyboardButton("Close", callback_data="close")])
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Choose sample media
    media_char = next((c for c in characters if is_video(c)), None) if rarity_mode == 'AMV' else next((c for c in characters if not is_video(c)), None)

    try:
        if media_char and media_char.get('img_url'):
            if update.message:
                if is_video(media_char):
                    await update.message.reply_video(media_char['img_url'], caption=harem_message, reply_markup=reply_markup)
                else:
                    await update.message.reply_photo(media_char['img_url'], caption=harem_message, reply_markup=reply_markup)
            elif update.callback_query:
                if is_video(media_char):
                    await update.callback_query.edit_message_media(
                        media=InputMediaVideo(media_char['img_url'], caption=harem_message),
                        reply_markup=reply_markup
                    )
                else:
                    await update.callback_query.edit_message_media(
                        media=InputMediaPhoto(media_char['img_url'], caption=harem_message),
                        reply_markup=reply_markup
                    )
        else:
            await (update.message or update.callback_query).reply_text(harem_message, reply_markup=reply_markup)
    except BadRequest:
        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)

# Pagination Handler
async def pagination_callback(update: Update, context: CallbackContext):
    page = int(update.callback_query.data.split(':')[1])
    await harem(update, context, page=page)

# Close Button
async def close_callback(update: Update, context: CallbackContext):
    await update.callback_query.message.delete()

# Register Handlers
application.add_handler(CommandHandler(["harem", "collection"], harem))
application.add_handler(CallbackQueryHandler(pagination_callback, pattern='^harem:'))
application.add_handler(CallbackQueryHandler(close_callback, pattern='^close$'))
