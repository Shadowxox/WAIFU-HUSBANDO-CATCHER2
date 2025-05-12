import random
from html import escape
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler, ChatMemberHandler

from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection

# Bot start time
bot_start_time = datetime.now()

# Media link
VIDEO_URL = "https://files.catbox.moe/c7lx2d.mp4"
GROUP_IMAGE_URL = "https://files.catbox.moe/tx0o73.jpg"

async def start(update: Update, context: CallbackContext) -> None:
    user = update.effective_user
    chat = update.effective_chat

    if not user:
        return

    user_data = await collection.find_one({"_id": user.id})
    if not user_data:
        await collection.insert_one({
            "_id": user.id,
            "first_name": user.first_name,
            "username": user.username
        })
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"New user started the bot.\nUser: <a href='tg://user?id={user.id}'>{escape(user.first_name)}</a>",
            parse_mode='HTML'
        )
    else:
        if user_data['first_name'] != user.first_name or user_data['username'] != user.username:
            await collection.update_one(
                {"_id": user.id},
                {"$set": {"first_name": user.first_name, "username": user.username}}
            )

    if chat.type == "private":
        await send_private_message(update, context)
    else:
        await send_group_message(update, context)

async def send_private_message(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("ADD ME", url='http://t.me/Dbz_waifubot?startgroup=true')],
        [InlineKeyboardButton("SUPPORT", url='https://t.me/hwkwjieie'), InlineKeyboardButton("UPDATES", url='https://t.me/DBZ_COMMUNITY2')],
        [InlineKeyboardButton("HELP", callback_data='help')],
        [InlineKeyboardButton("REPO", url='https://t.me/DBZ_ONGOING')]
    ]
    caption = """
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫    
 ✾ Yᴀᴛᴛᴀ~! Yᴏᴜ’ᴠᴇ Sᴜᴍᴍᴏɴᴇᴅ Mᴇ, Sᴇɴᴘᴀɪ!    
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┠ ➻ Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴡᴀᴋᴇɴᴇᴅ ꜰʀᴏᴍ ɪᴛꜱ ᴅɪɢɪᴛᴀʟ ꜱʟᴜᴍʙᴇʀ~  
┃     Rᴇᴀᴅʏ ᴛᴏ sᴇʀᴠᴇ ʏᴏᴜ ᴏɴ ᴀɴ ᴇᴘɪᴄ ᴊᴏᴜʀɴᴇʏ!  
┠ ➻ Wᴀɴɴᴀ ᴜɴʟᴏᴄᴋ ꜱᴇᴄʀᴇᴛ ᴄᴏᴍᴍᴀɴᴅꜱ?  
┃     Tᴀᴘ The Help, ᴏɴᴇɢᴀɪ~  
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
⏱ Bot Birth: 9 May 2025
    """
    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=VIDEO_URL,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def send_group_message(update: Update, context: CallbackContext) -> None:
    uptime = datetime.now() - bot_start_time
    caption = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫    
 ✾ Yᴀᴛᴛᴀ~! Yᴏᴜ’ᴠᴇ Sᴜᴍᴍᴏɴᴇᴅ Mᴇ, Sᴇɴᴘᴀɪ!    
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┠ ➻ Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴡᴀᴋᴇɴᴇᴅ ꜰʀᴏᴍ ɪᴛꜱ ᴅɪɢɪᴛᴀʟ ꜱʟᴜᴍʙᴇʀ~  
┃     Rᴇᴀᴅʏ ᴛᴏ sᴇʀᴠᴇ ʏᴏᴜ ᴏɴ ᴀɴ ᴇᴘɪᴄ ᴊᴏᴜʀɴᴇʏ!  
┠ ➻ Wᴀɴɴᴀ ᴜɴʟᴏᴄᴋ ꜱᴇᴄʀᴇᴛ ᴄᴏᴍᴍᴀɴᴅꜱ?  
┃     Tᴀᴘ ᴍʏ ᴘᴍ, ᴏɴᴇɢᴀɪ~  
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
⏱ Uptime: {str(timedelta(seconds=int(uptime.total_seconds())))}
    """
    keyboard = [
        [InlineKeyboardButton("ADD ME", url='http://t.me/Dbz_waifubot?startgroup=true')],
        [InlineKeyboardButton("SUPPORT", url='https://t.me/hwkwjieie'), InlineKeyboardButton("UPDATES", url='https://t.me/DBZ_COMMUNITY2')],
        [InlineKeyboardButton("HELP", callback_data='help')],
        [InlineKeyboardButton("REPO", url='https://t.me/DBZ_ONGOING')]
    ]
    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo=GROUP_IMAGE_URL,
        caption=caption,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await send_help_message(update, context)
    elif query.data == 'back':
        await send_private_message(update, context)

async def send_help_message(update: Update, context: CallbackContext) -> None:
    help_text = """
***┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫***    
✾ Hᴇʀᴇ’ꜱ Yᴏᴜʀ Gᴜɪᴅᴇ ᴛᴏ ᴛʜᴇ Oᴛᴀᴋᴜ Rᴇᴀʟᴍ~    
***┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫***
➻ /guess – Group-only anime guessing game
➻ /fav – Set favorite waifu/husbando
➻ /trade – Propose a trade
➻ /gift – Gift a character
➻ /collection – Show your collection
➻ /topgroups – Group leaderboard
➻ /top – Top users
➻ /ctop – Chat leaderboard
➻ /changetime – Control timing (group only)
    """
    keyboard = [[InlineKeyboardButton("⤾ Back", callback_data='back')]]
    await context.bot.edit_message_caption(
        chat_id=update.effective_chat.id,
        message_id=update.callback_query.message.message_id,
        caption=help_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

# Handle when bot is added to a group
async def bot_added(update: Update, context: CallbackContext) -> None:
    member = update.my_chat_member
    if member.new_chat_member.status in ("member", "administrator"):
        chat = member.chat
        uptime = datetime.now() - bot_start_time
        caption = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫    
 ✾ Yᴀᴛᴛᴀ~! Yᴏᴜ’ᴠᴇ Sᴜᴍᴍᴏɴᴇᴅ Mᴇ, Sᴇɴᴘᴀɪ!    
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┠ ➻ Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴡᴀᴋᴇɴᴇᴅ ꜰʀᴏᴍ ɪᴛꜱ ᴅɪɢɪᴛᴀʟ ꜱʟᴜᴍʙᴇʀ~  
┃     Rᴇᴀᴅʏ ᴛᴏ sᴇʀᴠᴇ ʏᴏᴜ ᴏɴ ᴀɴ ᴇᴘɪᴄ ᴊᴏᴜʀɴᴇʏ!  
┠ ➻ Wᴀɴɴᴀ ᴜɴʟᴏᴄᴋ ꜱᴇᴄʀᴇᴛ ᴄᴏᴍᴍᴀɴᴅꜱ?  
┃     Tᴀᴘ ᴍʏ ᴘᴍ, ᴏɴᴇɢᴀɪ~  
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
⏱ Uptime: {str(timedelta(seconds=int(uptime.total_seconds())))}
        """
        keyboard = [
            [InlineKeyboardButton("ADD ME", url='http://t.me/Dbz_waifubot?startgroup=true')],
            [InlineKeyboardButton("SUPPORT", url='https://t.me/hwkwjieie'), InlineKeyboardButton("UPDATES", url='https://t.me/DBZ_COMMUNITY2')],
            [InlineKeyboardButton("HELP", callback_data='help')],
            [InlineKeyboardButton("REPO", url='https://t.me/DBZ_ONGOING')]
        ]
        try:
            await context.bot.send_photo(
                chat_id=chat.id,
                photo=GROUP_IMAGE_URL,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            print(f"[GROUP WELCOME FAILED] {chat.id}: {e}")

# Register handlers
application.add_handler(CommandHandler("start", start, block=False))
application.add_handler(CallbackQueryHandler(button, pattern="^(help|back)$", block=False))
application.add_handler(ChatMemberHandler(bot_added, chat_member_types=["my_chat_member"]))
