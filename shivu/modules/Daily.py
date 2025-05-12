import datetime
import asyncio
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from shivu import application, user_collection

OWNER_ID = 7795212861
GROUPS_AUTO_DELETE = [-1002264558318, -1002643948280]

# /rcoinall - Only usable by the owner to reset a replied user's coin balance to zero
async def rcoinall(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("❗Please reply to the user's message you want to reset coins for.")
        return

    target_user = update.message.reply_to_message.from_user.id
    await user_collection.update_one({"id": target_user}, {"$set": {"coins": 0}}, upsert=True)
    await update.message.reply_text("✅ User's coin balance has been reset to 0.")

# /daily - Claim daily coins
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

# /weekly - Claim weekly coins
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

# /profile - Show user profile
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

# Register command handlers
application.add_handler(CommandHandler("rcoinall", rcoinall))
application.add_handler(CommandHandler("daily", daily))
application.add_handler(CommandHandler("weekly", weekly))
application.add_handler(CommandHandler("profile", profile))
