import random
import string
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from shivu import application, user_collection, waifu_collection 

# Constants
SHOP_COSTS = {
    "🔱 Rare": 500,
    "🌀 Medium": 1000,
    "🦄 Legendary": 5000,
    "💮 Special Edition": 10000,
    "🔮 Limited Edition": 20000,
    "🎐 Celestial": 25000,
    "🎭 X Verse": 35000,
    "🔞 Erotic": 80000,
    "💞 Valentine Special": 45000,
    "❄️ Winter Special": 48000,
    "🌤️ Summer Special": 50000,
    "🎃 Halloween Special": 46000,
    "🎴 AMV": 145000,
    "🎥 Hollywood": 150000
}
RARITY_KEYS = list(SHOP_COSTS.keys())
SHOP_USER_STATE = {}
AUTO_DELETE_GROUPS = [-1002264558318, -1002643948280]

# Utils
def generate_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# /shop command
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(rarity, callback_data=f"rarity_{rarity}")] for rarity in RARITY_KEYS]
    await update.message.reply_text("🎡 Choose a rarity to spin:", reply_markup=InlineKeyboardMarkup(keyboard))

# Callback for shop
async def shop_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("rarity_"):
        rarity = data.split("rarity_")[1]
        SHOP_USER_STATE[user_id] = rarity

        try:
            keyboard = [[InlineKeyboardButton("✅ Confirm", callback_data="confirm_spin")]]
try:
    await context.bot.send_message(chat_id=user_id, text="✅ Tap confirm below to get your waifu spin code in PM.")
    await query.edit_message_text(
    text="""🔐 Please tap *Confirm* in bot PM after messaging it.

🔁 Use /start in private if you haven’t already.

🛑 *NOTE:* Code will be given in private only.

🔵 पर्सनल में बॉट को मैसेज करो और फिर Confirm दबाओ। Code वहीं मिलेगा।""",
    parse_mode="Markdown",
    reply_markup=InlineKeyboardMarkup(keyboard)
)
    
except:
    await query.edit_message_text("❌ Please start the bot in PM first using /start, then try again.")

        except:
            await query.edit_message_text("❌ Please start the bot in PM first.")

    elif data == "confirm_spin":
        chat_type = query.message.chat.type
        if chat_type != "private":
            await query.answer("❗ Confirm in PM/DM only.", show_alert=True)
            return

        rarity = SHOP_USER_STATE.get(user_id)
        if not rarity:
            await query.answer("Please select a rarity first.", show_alert=True)
            return

        cost = SHOP_COSTS.get(rarity, 0)
        user = await user_collection.find_one({"id": user_id})
        balance = user.get("coins", 0) if user else 0

        if balance < cost:
            await query.edit_message_text("❌ Not enough coins to spin.")
            return

        await user_collection.update_one({"id": user_id}, {"$inc": {"coins": -cost}}, upsert=True)
        waifus = waifu_collection.find({"caption": {"$regex": f"(?i)Rarity: {rarity}"}})
        waifu_list = [w async for w in waifus]
        if not waifu_list:
            await query.edit_message_text("No waifus found for this rarity.")
            return

        waifu = random.choice(waifu_list)
        waifu_id = waifu["caption"].split("ID:")[-1].strip()
        code = generate_code()
        await context.bot.send_message(chat_id=user_id, text=f"🎁 Your waifu spin is ready! Code: `{code}`\n(Use in waifu claim logic)", parse_mode="Markdown")
        await query.edit_message_text("✅ Code has been sent to your DM/PM.")

# /daily
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await user_collection.find_one({"id": user_id}) or {}
    now = datetime.datetime.utcnow()
    last_daily = user.get("last_daily")

    if last_daily:
        last_time = datetime.datetime.fromisoformat(last_daily)
        if (now - last_time).total_seconds() < 86400:
            remaining = 86400 - (now - last_time).total_seconds()
            hours = int(remaining // 3600)
            minutes = int((remaining % 3600) // 60)
            return await update.message.reply_text(f"🕒 You can claim daily reward in {hours}h {minutes}m.")

    await user_collection.update_one(
        {"id": user_id},
        {"$set": {"last_daily": now.isoformat()}, "$inc": {"coins": 100}},
        upsert=True
    )
    await update.message.reply_text("✅ You claimed 100 daily coins!")

# /weekly
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await user_collection.find_one({"id": user_id}) or {}
    now = datetime.datetime.utcnow()
    last_weekly = user.get("last_weekly")

    if last_weekly:
        last_time = datetime.datetime.fromisoformat(last_weekly)
        if (now - last_time).total_seconds() < 604800:
            remaining = 604800 - (now - last_time).total_seconds()
            days = int(remaining // 86400)
            hours = int((remaining % 86400) // 3600)
            return await update.message.reply_text(f"🕒 You can claim weekly reward in {days}d {hours}h.")

    await user_collection.update_one(
        {"id": user_id},
        {"$set": {"last_weekly": now.isoformat()}, "$inc": {"coins": 1000}},
        upsert=True
    )
    await update.message.reply_text("✅ You claimed 1000 weekly coins!")

# /profile
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    chat_id = update.effective_chat.id

    db_user = await user_collection.find_one({"id": user_id}) or {}
    coins = db_user.get("coins", 0)
    waifus = db_user.get("waifus", [])
    favorites = db_user.get("favorites", [])
    waifu_count = len(set(waifus)) if isinstance(waifus, list) else 0

    fav_names = []
    for waifu_id in favorites[:3]:
        waifu = await waifu_collection.find_one({"caption": {"$regex": f"ID: {waifu_id}$"}})
        if waifu:
            try:
                name_line = waifu["caption"].split("\n")[0]
                name = name_line.split(":", 1)[-1].strip()
                fav_names.append(name)
            except:
                pass

    fav_text = "None"
    if fav_names:
        fav_text = "\n".join([f"• {name}" for name in fav_names])

    text = (
        f"👤 **Profile**\n"
        f"• Name: `{user.first_name}`\n"
        f"• ID: `{user_id}`\n"
        f"• 💰 Coins: `{coins}`\n"
        f"• 💠 Waifus Collected: `{waifu_count}`\n"
        f"• ⭐ Favorite Waifus:\n{fav_text}"
    )

    sent = await update.message.reply_text(text, parse_mode="Markdown")

    if chat_id in AUTO_DELETE_GROUPS:
        await context.bot.delete_message(chat_id=chat_id, message_id=update.message.message_id)
        await context.bot.delete_message(chat_id=chat_id, message_id=sent.message_id, timeout=10)

# Register handlers
application.add_handler(CommandHandler("shop", shop))
application.add_handler(CallbackQueryHandler(shop_button, pattern="^(rarity_|confirm_spin)"))
application.add_handler(CommandHandler("daily", daily))
application.add_handler(CommandHandler("weekly", weekly))
application.add_handler(CommandHandler("profile", profile))
