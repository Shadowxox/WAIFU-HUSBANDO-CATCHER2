from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from html import escape
from shivu import user_collection, application
from telegram.constants import ParseMode

# Updated rarity mapping
RARITY_MAP = {
    1: "🔱 Rare",
    2: "🌀 Medium",
    3: "🦄 Legendary",
    4: "💮 Special Edition",
    5: "🔮 Limited Edition",
    6: "🌐 Celestial",
    7: "🔞 Erotic",
    8: "💖 Valentine Special",
    9: "🎝 X Verse",
    10: "🎃 Halloween Special",
    11: "❄️ Winter Special",
    12: "🌤️ Summer Special",
    13: "🎴 AMV",
    14: "🎮 Hollywood"
}

AMV_RARITIES = ["🎴 AMV", "🎬 Hollywood"]

async def harem(update: Update, context: CallbackContext, mode="harem") -> None:
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user or 'characters' not in user:
        await update.message.reply_text("You have no characters yet.")
        return

    grouped = {}
    for char in user['characters']:
        char_id = char['id']
        char['rarity'] = RARITY_MAP.get(char.get('rarity', 1), "Unknown")
        if mode == "harem" and char['rarity'] in AMV_RARITIES:
            continue
        if mode == "amv" and char['rarity'] not in AMV_RARITIES:
            continue
        if char_id not in grouped:
            grouped[char_id] = {**char, 'count': 1}
        else:
            grouped[char_id]['count'] += 1

    if not grouped:
        await update.message.reply_text("No characters found for this view.")
        return

    msg = f"<b>{escape(update.effective_user.first_name)}'s {'Harem' if mode == 'harem' else 'AMV Collection'}</b>\n\n"
    for char in grouped.values():
        rarity = char['rarity']
        msg += f"<b>‴</b> <code>{char['id']}</code> - {char['name']} ×{char['count']} <i>({rarity})</i>\n"

    keyboard = [
        [
            InlineKeyboardButton("📷 Harem", callback_data="view:harem"),
            InlineKeyboardButton("🎥 AMV", callback_data="view:amv")
        ],
        [InlineKeyboardButton("Close", callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

async def view_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    _, mode = query.data.split(":")
    await query.answer()
    await query.message.delete()
    await harem(update, context, mode)

application.add_handler(CommandHandler(["harem", "collection"], harem))
application.add_handler(CallbackQueryHandler(view_callback, pattern=r"^view:"))
application.add_handler(CallbackQueryHandler(lambda u, c: u.callback_query.message.delete(), pattern="^close$"))
