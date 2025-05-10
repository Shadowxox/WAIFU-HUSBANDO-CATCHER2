import os
import logging
import random
from html import escape
from datetime import datetime, timedelta

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from motor.motor_asyncio import AsyncIOMotorClient

# -------------------- Configuration --------------------
BOT_TOKEN = os.getenv("BOT_TOKEN")  # Your bot token
GROUP_ID = int(os.getenv("GROUP_ID", "0"))  # Your group ID for notifications
SUPPORT_CHAT = os.getenv("SUPPORT_CHAT", "@hwkwjieie")
UPDATE_CHAT = os.getenv("UPDATE_CHAT", "@DBZ_COMMUNITY2")
BOT_USERNAME = os.getenv("BOT_USERNAME", "Dbz_waifubot")
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

# -------------------- Logging Setup --------------------
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# -------------------- Database Setup --------------------
mongo_client = AsyncIOMotorClient(MONGO_URI)
db = mongo_client["waifu_db"]
collection = db["pm_users"]

# -------------------- Bot Application --------------------
application = ApplicationBuilder().token(BOT_TOKEN).build()

# -------------------- Bot State --------------------
bot_start_time = datetime.now()

# -------------------- Media URLs --------------------
VIDEO_URL = "https://files.catbox.moe/c7lx2d.mp4"
PHOTO_URLS = [
    "https://files.catbox.moe/tx0o73.jpg",
    "https://files.catbox.moe/h0qot3.jpg",
    "https://i.ibb.co/Kcxbdcm4/image.jpg",
]

def get_random_photo_url():
    return random.choice(PHOTO_URLS)

# -------------------- Command Handlers --------------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat

    # Record user info in database
    user_data = await collection.find_one({"_id": user.id})
    if user_data is None:
        await collection.insert_one({"_id": user.id, "first_name": user.first_name, "username": user.username})
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=(f"New user started the bot.\n"
                  f"User: <a href='tg://user?id={user.id}'>{escape(user.first_name)}</a>"),
            parse_mode="HTML"
        )
    else:
        if user_data.get("first_name") != user.first_name or user_data.get("username") != user.username:
            await collection.update_one(
                {"_id": user.id},
                {"$set": {"first_name": user.first_name, "username": user.username}}
            )

    # Send appropriate welcome
    if chat.type == "private":
        await send_private_message(update, context)
    else:
        await send_group_message(update, context)

async def send_private_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    caption = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
        "  ✾ Yᴀᴛᴛᴀ~! Yᴏᴜ’ᴠᴇ Sᴜᴍᴍᴏɴᴇᴅ Mᴇ, Sᴇɴᴘᴀɪ!\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
        "┠ ➻ Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴡᴀᴋᴇɴᴇᴅ...\n"
        "┃   Ready to serve you!\n"
        "┠ ➻ Wanna unlock secret commands? Tap Help!\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
        "⏱ Bot Birth: Just born 9 May"
    )
    keyboard = [
        [InlineKeyboardButton("ADD ME", url=f"http://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("SUPPORT", url=SUPPORT_CHAT), InlineKeyboardButton("UPDATES", url=UPDATE_CHAT)],
        [InlineKeyboardButton("HELP", callback_data="help")],
        [InlineKeyboardButton("REPO", url="https://t.me/DBZ_ONGOING")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=VIDEO_URL,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def send_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    uptime = datetime.now() - bot_start_time
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    caption = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
        "  ✾ Yᴀᴛᴛᴀ~! Yᴏᴜ’ᴠᴇ Sᴜᴍᴍᴏɴᴇᴅ Mᴇ...\n"
        f"Bot Uptime: {uptime_str}\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫"
    )
    keyboard = [
        [InlineKeyboardButton("ADD ME", url=f"http://t.me/{BOT_USERNAME}?startgroup=true")],
        [InlineKeyboardButton("SUPPORT", url=SUPPORT_CHAT), InlineKeyboardButton("UPDATES", url=UPDATE_CHAT)],
        [InlineKeyboardButton("HELP", callback_data="help")],
        [InlineKeyboardButton("REPO", url="https://t.me/DBZ_ONGOING")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Fallback to photo in groups
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=get_random_photo_url(),
        caption=caption,
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == "help":
        await send_help_message(update, context)
    elif query.data == "back":
        await send_private_message(update, context)

async def send_help_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    help_text = (
        "┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
        "  ✾ Help Guide to the Otaku Realm!\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫\n"
        "➻ /guess – Guess characters (group-only)\n"
        "➻ /fav – Set your waifu/husbando favorite\n"
        "➻ /trade – Trade with fellow collectors\n"
        "➻ /gift – Gift a character (groups)\n"
        "➻ /collection – View your collection\n"
        "➻ /topgroups – Top groups leaderboard\n"
        "➻ /top – Global top collectors\n"
        "➻ /ctop – Chat-specific leaderboard\n"
        "➻ /changetime – Change spawn frequency (group-only)"
    )
    keyboard = [[InlineKeyboardButton("⤾ Back", callback_data="back")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.edit_message_caption(
        chat_id=update.effective_chat.id,
        message_id=update.callback_query.message.message_id,
        caption=help_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

# -------------------- Handler Registration --------------------
application.add_handler(CommandHandler("start", start))
application.add_handler(CallbackQueryHandler(button_handler, pattern="^help$|^back$"))

# -------------------- Run Bot --------------------
if __name__ == "__main__":
    application.run_polling()
