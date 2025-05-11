from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update, InputMediaVideo, InputMediaPhoto
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from collections import defaultdict
import asyncio

# Simulated database
user_collection = ...  # your MongoDB or other storage client
user_favorites = defaultdict(str)  # user_id -> character_id

RARITY_NAMES = {
    11: 'Erotic',
    12: 'AMV',
    13: 'Hollywood'
}

async def fav(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if len(context.args) != 1:
        await update.message.reply_text("Usage: /fav <character_id>")
        return

    fav_id = context.args[0]
    user = await user_collection.find_one({'id': user_id})

    if not user:
        await update.message.reply_text("You don't have any characters yet.")
        return

    character = next((c for c in user['characters'] if c['id'] == fav_id), None)
    if not character:
        await update.message.reply_text("Character not found in your collection.")
        return

    user_favorites[user_id] = fav_id
    await update.message.reply_text(f"✅ Character with ID {fav_id} set as your favorite!")


def _group_characters(characters):
    grouped = {}
    for c in characters:
        key = (c['id'], c['rarity'])
        if key not in grouped:
            grouped[key] = {'id': c['id'], 'names': [c['name']], 'rarity': c['rarity'], 'count': 1}
        else:
            grouped[key]['count'] += 1
            if c['name'] not in grouped[key]['names']:
                grouped[key]['names'].append(c['name'])
    return list(grouped.values())


def _build_harem_message(grouped_characters):
    message_lines = []
    for c in grouped_characters:
        rarity_label = RARITY_NAMES.get(c['rarity'], str(c['rarity']))
        line = f"ID: {c['id']}\nName(s): {', '.join(c['names'])}\nCount: {c['count']}\nRarity: {rarity_label}\n"
        message_lines.append(line)
    return '\n'.join(message_lines)


def _build_harem_buttons():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("See Collection", callback_data='collection'),
            InlineKeyboardButton("🎞 AMV", callback_data='amv')
        ]
    ])


async def _send_text_message(update: Update, text: str, reply_markup: InlineKeyboardMarkup):
    if update.message:
        await update.message.reply_text(text=text, reply_markup=reply_markup)
    else:
        try:
            await update.callback_query.edit_message_text(text=text, reply_markup=reply_markup)
        except:
            pass


async def harem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})
    if not user or 'characters' not in user or not user['characters']:
        await _send_text_message(update, "You don't have any characters yet.", None)
        return

    grouped = _group_characters(user['characters'])
    harem_message = _build_harem_message(grouped)
    reply_markup = _build_harem_buttons()

    fav_character_id = user_favorites.get(user_id)
    if fav_character_id:
        fav_character = next((c for c in user['characters'] if c['id'] == fav_character_id), None)
        if fav_character:
            if 'video_url' in fav_character:
                if update.message:
                    await update.message.reply_video(video=fav_character['video_url'], caption=harem_message, reply_markup=reply_markup)
                else:
                    try:
                        await update.callback_query.edit_message_media(
                            media=InputMediaVideo(media=fav_character['video_url'], caption=harem_message),
                            reply_markup=reply_markup
                        )
                    except:
                        await _send_text_message(update, harem_message, reply_markup)
                return
            elif 'img_url' in fav_character:
                if update.message:
                    await update.message.reply_photo(photo=fav_character['img_url'], caption=harem_message, reply_markup=reply_markup)
                else:
                    try:
                        await update.callback_query.edit_message_caption(caption=harem_message, reply_markup=reply_markup)
                    except:
                        await update.callback_query.edit_message_reply_markup(reply_markup=reply_markup)
                return

    await _send_text_message(update, harem_message, reply_markup)


async def inline_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    user = await user_collection.find_one({'id': user_id})
    if not user or 'characters' not in user:
        await query.edit_message_text("No collection found.")
        return

    if query.data == 'collection':
        await harem(update, context)

    elif query.data == 'amv':
        amv_videos = [
            c for c in user['characters']
            if c.get('rarity') in [12, 13] and 'video_url' in c
        ]
        if not amv_videos:
            await query.edit_message_text("You have no AMV or Hollywood videos.")
            return

        video = amv_videos[0]  # or cycle/random choice
        try:
            await query.edit_message_media(
                media=InputMediaVideo(media=video['video_url'], caption=f"🎞 {video['name']} - {RARITY_NAMES.get(video['rarity'], video['rarity'])}"),
                reply_markup=_build_harem_buttons()
            )
        except:
            await query.edit_message_text("Failed to load video.")


def setup_handlers(application):
    application.add_handler(CommandHandler("harem", harem))
    application.add_handler(CommandHandler("fav", fav))
    application.add_handler(CallbackQueryHandler(inline_handler))
