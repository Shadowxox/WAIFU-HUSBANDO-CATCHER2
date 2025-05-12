import random
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from shivu import application, user_collection

# List of images to randomly select for /cointop
TOP_IMAGES = [
    "https://files.catbox.moe/tx0o73.jpg",
    "https://files.catbox.moe/h0qot3.jpg",
    "https://i.ibb.co/Kcxbdcm4/image.jpg"
]

# /bal and /balance command
async def balance_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    else:
        user = update.effective_user

    user_data = await user_collection.find_one({"id": user.id})
    coins = user_data.get("coins", 0) if user_data else 0

    if update.message.reply_to_message:
        await update.message.reply_text(f"💰 {user.first_name} has {coins} coins.")
    else:
        await update.message.reply_text(f"💰 You have {coins} coins.")

# /cointop command
async def cointop_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    top_users = user_collection.find({"coins": {"$gt": 0}}).sort("coins", -1).limit(10)
    leaderboard = [user async for user in top_users]

    if not leaderboard:
        await update.message.reply_text("❌ No users with coins found.")
        return

    msg = "🏆 *Top 10 Richest Users:*\n"
    for i, user in enumerate(leaderboard, start=1):
        name = f"[User](tg://user?id={user['id']})"
        msg += f"{i}. {name} — `{user.get('coins', 0)}` coins\n"

    image_url = random.choice(TOP_IMAGES)
    await update.message.reply_photo(photo=image_url, caption=msg, parse_mode="Markdown")

# Register the handlers
application.add_handler(CommandHandler(["bal", "balance"], balance_command))
application.add_handler(CommandHandler("cointop", cointop_command))
