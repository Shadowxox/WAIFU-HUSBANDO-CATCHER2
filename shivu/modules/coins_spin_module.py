import random
import string
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes
from shivu import application, user_collection, waifu_collection

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
SPIN_CODES = {}

def generate_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

# /shop command
async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(rarity, callback_data=f"rarity_{rarity}")] for rarity in RARITY_KEYS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎡 Choose a rarity to spin:", reply_markup=reply_markup)

# Spin confirmation handler
async def shop_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    if data.startswith("rarity_"):
        rarity = data.split("rarity_")[1]
        SHOP_USER_STATE[user_id] = rarity

        keyboard = [[InlineKeyboardButton("✅ Confirm", callback_data="confirm_spin")]]
        await query.edit_message_text(
            text="🔐 Please tap confirm after messaging the bot in DM/PM.\n\n"
                 "🔁 /start in private if not started.\n\n"
                 "🛑 *NOTE:* Code will be given in private only.\n\n"
                 "🔵 पर्सनल में बॉट को मैसेज करो और फिर Confirm दबाओ। Code वहीं मिलेगा।",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "confirm_spin":
        if query.message.chat.type != "private":
            await query.answer("❗ Confirm in PM/DM only.", show_alert=True)
            return

        rarity = SHOP_USER_STATE.get(user_id)
        if not rarity:
            await query.answer("Please select a rarity first.", show_alert=True)
            return

        cost = SHOP_COSTS.get(rarity, 0)
        user = await user_collection.find_one({"id": user_id}) or {}
        balance = user.get("coins", 0)

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
        await user_collection.update_one({"id": user_id}, {"$addToSet": {"waifus": waifu_id}}, upsert=True)

        await context.bot.send_message(chat_id=user_id, text="🎁 Waifu added to your collection!")
        await query.edit_message_text("✅ Waifu successfully granted!")

# /daily command
async def daily(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await user_collection.find_one({"id": user_id}) or {}

    last_claim = user.get("last_daily")
    now = datetime.datetime.utcnow()

    if last_claim and (now - last_claim).total_seconds() < 86400:
        remaining = 86400 - (now - last_claim).total_seconds()
        hours, rem = divmod(remaining, 3600)
        minutes = rem // 60
        await update.message.reply_text(f"🕒 You can claim daily again in {int(hours)}h {int(minutes)}m.")
        return

    await user_collection.update_one({"id": user_id}, {"$set": {"last_daily": now}, "$inc": {"coins": 100}}, upsert=True)
    await update.message.reply_text("✅ You claimed your daily reward of 💰100 coins!")

# /weekly command
async def weekly(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = await user_collection.find_one({"id": user_id}) or {}

    last_claim = user.get("last_weekly")
    now = datetime.datetime.utcnow()

    if last_claim and (now - last_claim).total_seconds() < 604800:
        remaining = 604800 - (now - last_claim).total_seconds()
        days = int(remaining // 86400)
        hours = int((remaining % 86400) // 3600)
        await update.message.reply_text(f"🕒 You can claim weekly again in {days}d {hours}h.")
        return

    await user_collection.update_one({"id": user_id}, {"$set": {"last_weekly": now}, "$inc": {"coins": 1000}}, upsert=True)
    await update.message.reply_text("✅ You claimed your weekly reward of 💰1000 coins!")

# /profile command
GROUPS_AUTO_DELETE = [-1002264558318, -1002643948280]

async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    data = await user_collection.find_one({"id": user_id}) or {}

    coins = data.get("coins", 0)
    waifu_ids = data.get("waifus", [])
    waifu_count = len(waifu_ids)
    favorites = data.get("favs", [])

    favs = "\n".join([f"• {name}" for name in favorites]) if favorites else "No favorites yet."

    msg = await update.message.reply_text(
        f"👤 Profile of {user.mention_html()}\n\n"
        f"💰 Coins: {coins}\n"
        f"👩‍❤️‍💋‍👨 Waifus: {waifu_count}\n"
        f"❤️ Favorites:\n{favs}",
        parse_mode="HTML"
    )

    if update.effective_chat.id in GROUPS_AUTO_DELETE:
        await asyncio.sleep(30)
        try:
            await msg.delete()
        except:
            pass

# Register handlers
application.add_handler(CommandHandler("shop", shop))
application.add_handler(CallbackQueryHandler(shop_button, pattern="^(rarity_|confirm_spin)"))
application.add_handler(CommandHandler("daily", daily))
application.add_handler(CommandHandler("weekly", weekly))
application.add_handler(CommandHandler("profile", profile))
