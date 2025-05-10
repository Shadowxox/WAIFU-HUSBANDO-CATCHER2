from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, CallbackContext
from html import escape
from shivu import user_collection, application
from telegram.constants import ParseMode

# Rarity Mapping
RARITY_MAP = {
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

AMV_RARITIES = ["🎴 AMV", "🎥 Hollywood"]

def get_rarity_label(rarity_key):
    return RARITY_MAP.get(rarity_key, f"❔ Unknown")

async def harem(update: Update, context: CallbackContext, mode="harem") -> None:
    user_id = update.effective_user.id
    user = await user_collection.find_one({'id': user_id})

    if not user or 'characters' not in user:
        await update.message.reply_text("You have no characters yet.")
        return

    grouped = {}
    for char in user['characters']:
        rarity_label = get_rarity_label(char.get('rarity'))
        if mode == "harem" and rarity_label in AMV_RARITIES:
            continue
        if mode == "amv" and rarity_label not in AMV_RARITIES:
            continue

        char_id = char['id']
        if char_id not in grouped:
            grouped[char_id] = {
                'id': char_id,
                'names': [char['name']],
                'rarity': rarity_label,
                'count': 1
            }
        else:
            grouped[char_id]['count'] += 1
            if char['name'] not in grouped[char_id]['names']:
                grouped[char_id]['names'].append(char['name'])

    if not grouped:
        await update.message.reply_text("No characters found for this view.")
        return

    title = f"{escape(update.effective_user.first_name)}'s {'Harem' if mode == 'harem' else 'AMV Collection'}"
    msg = f"<b>{title}</b>\n\n"
    for char in grouped.values():
        rarity_emoji = char['rarity'].split()[0]
        names = " , ".join(char['names'])
        msg += f"◇{rarity_emoji}│<code>{char['id']}</code> {names} ×{char['count']}\n"

    keyboard = [
        [
            InlineKeyboardButton("📷 Harem", callback_data="view:harem"),
            InlineKeyboardButton("🎥 AMV", callback_data="view:amv")
        ],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(msg, parse_mode=ParseMode.HTML, reply_markup=reply_markup)

# Callback Query Handler
async def view_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    _, mode = query.data.split(":")
    await query.answer()
    await query.message.delete()
    await harem(update, context, mode)

async def close_callback(update: Update, context: CallbackContext):
    await update.callback_query.message.delete()

# Register Handlers
application.add_handler(CommandHandler(["harem", "collection"], harem))
application.add_handler(CallbackQueryHandler(view_callback, pattern=r"^view:"))
application.add_handler(CallbackQueryHandler(close_callback, pattern="^close$"))
