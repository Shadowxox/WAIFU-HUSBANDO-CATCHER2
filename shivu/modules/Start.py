import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from datetime import datetime, timedelta

from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection

# Record the bot start time
bot_start_time = datetime.now()

# Video URL to send on /start
VIDEO_URL = "https://files.catbox.moe/c7lx2d.mp4"

async def start(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    first_name = update.effective_user.first_name
    username = update.effective_user.username

    user_data = await collection.find_one({"_id": user_id})

    if user_data is None:
        await collection.insert_one({"_id": user_id, "first_name": first_name, "username": username})
        await context.bot.send_message(
            chat_id=GROUP_ID,
            text=f"New user started the bot.\nUser: <a href='tg://user?id={user_id}'>{escape(first_name)}</a>",
            parse_mode='HTML'
        )
    else:
        if user_data['first_name'] != first_name or user_data['username'] != username:
            await collection.update_one({"_id": user_id}, {"$set": {"first_name": first_name, "username": username}})

    if update.effective_chat.type == "private":
        await send_private_message(update, context)
    else:
        await send_group_message(update, context)

async def send_private_message(update: Update, context: CallbackContext) -> None:
    caption = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫    
  ✾ Yᴀᴛᴛᴀ~! Yᴏᴜ’ᴠᴇ Sᴜᴍᴍᴏɴᴇᴅ Mᴇ, Sᴇɴᴘᴀɪ!    
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┠ ➻ Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴡᴀᴋᴇɴᴇᴅ ꜰʀᴏᴍ ɪᴛꜱ ᴅɪɢɪᴛᴀʟ ꜱʟᴜᴍʙᴇʀ~  
┃       Rᴇᴀᴅʏ ᴛᴏ sᴇʀᴠᴇ ʏᴏᴜ ᴏɴ ᴀɴ ᴇᴘɪᴄ ᴊᴏᴜʀɴᴇʏ!  
┠ ➻ Wᴀɴɴᴀ ᴜɴʟᴏᴄᴋ ʜɪᴅᴅᴇɴ ꜰᴇᴀᴛᴜʀᴇꜱ ᴏʀ sᴇᴄʀᴇᴛ ᴄᴏᴍᴍᴀɴᴅꜱ?  
┃       Tᴀᴘ The Help, ᴏɴᴇɢᴀɪ~  
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
    ⏱ Bot Birth: Jᴜꜱᴛ ʙᴏʀɴ ɪɴᴛᴏ ᴛʜɪꜱ ᴡᴏʀʟᴅ 9 may
    """
    keyboard = [
        [InlineKeyboardButton("ADD ME", url='http://t.me/Dbz_waifubot?startgroup=true')],
        [InlineKeyboardButton("SUPPORT", url='https://t.me/hwkwjieie'), InlineKeyboardButton("UPDATES", url='https://t.me/DBZ_COMMUNITY2')],
        [InlineKeyboardButton("HELP", callback_data='help')],
        [InlineKeyboardButton("REPO", url='https://t.me/DBZ_ONGOING')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_video(
        chat_id=update.effective_chat.id,
        video=VIDEO_URL,
        caption=caption,
        reply_markup=reply_markup,
        parse_mode='markdown'
    )

async def send_group_message(update: Update, context: CallbackContext) -> None:
    current_time = datetime.now()
    uptime = current_time - bot_start_time
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    caption = f"""
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫    
  ✾ Yᴀᴛᴛᴀ~! Yᴏᴜ’ᴠᴇ Sᴜᴍᴍᴏɴᴇᴅ Mᴇ, Sᴇɴᴘᴀɪ!    
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
┠ ➻ Tʜᴇ ʙᴏᴛ ʜᴀꜱ ᴀᴡᴀᴋᴇɴᴇᴅ ꜰʀᴏᴍ ɪᴛꜱ ᴅɪɢɪᴛᴀʟ ꜱʟᴜᴍʙᴇʀ~  
┃       Rᴇᴀᴅʏ ᴛᴏ sᴇʀᴠᴇ ʏᴏᴜ ᴏɴ ᴀɴ ᴇᴘɪᴄ ᴊᴏᴜʀɴᴇʏ!  
┠ ➻ Wᴀɴɴᴀ ᴜɴʟᴏᴄᴋ ʜɪᴅᴅᴇɴ ꜰᴇᴀᴛᴜʀᴇꜱ ᴏʀ sᴇᴄʀᴇᴛ ᴄᴏᴍᴍᴀɴᴅꜱ?  
┃       Tᴀᴘ ᴍʏ ᴘᴍ, ᴏɴᴇɢᴀɪ~  
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
    ⏱ Bot Uptime: {uptime_str}
    """
    keyboard = [
        [InlineKeyboardButton("ADD ME", url='http://t.me/Dbz_waifubot?startgroup=true')],
        [InlineKeyboardButton("SUPPORT", url='https://t.me/hwkwjieie'), InlineKeyboardButton("UPDATES", url='https://t.me/DBZ_COMMUNITY2')],
        [InlineKeyboardButton("HELP", callback_data='help')],
        [InlineKeyboardButton("REPO", url='https://t.me/DBZ_ONGOING')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(
        chat_id=update.effective_chat.id,
        photo="https://files.catbox.moe/tx0o73.jpg",  # fallback image
        caption=caption,
        reply_markup=reply_markup
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
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
➻ /guess – Gʀᴏᴜᴘ-ᴏɴʟʏ. Cʟᴀɪᴍ ᴀɴɪᴍᴇ ᴄʜᴀʀᴀᴄᴛᴇʀꜱ!
➻ /fav – Sᴇᴛ ʏᴏᴜʀ ꜰᴀᴠᴏʀɪᴛᴇ ᴡᴀɪꜰᴜ/ʜᴜꜱʙᴀɴᴅᴏ~
➻ /trade – Pʀᴏᴘᴏꜱᴇ ᴀ ᴛʀᴀᴅᴇ ᴛᴏ ꜰᴇʟʟᴏᴡ ᴄᴏʟʟᴇᴄᴛᴏʀꜱ~
➻ /gift – Gɪꜰᴛ ᴀ ᴄʜᴀʀᴀᴄᴛᴇʀ ɪɴ ɢʀᴏᴜᴘꜱ~
➻ /collection – Yᴏᴜʀ ᴀɴɪᴍᴇ ᴛʀᴇᴀꜱᴜʀᴇ~
➻ /topgroups – Tᴏᴘ ɢʀᴏᴜᴘ ʟᴇᴀᴅᴇʀꜱ!
➻ /top – Tᴏᴘ ᴜꜱᴇʀꜱ
➻ /ctop – Cʜᴀᴛ ʟᴇᴀᴅᴇʀʙᴏᴀʀᴅ!
➻ /changetime – Gʀᴏᴜᴘ ᴏɴʟʏ ᴛɪᴍᴇ ᴄᴏɴᴛʀᴏʟ
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
    """
    help_keyboard = [[InlineKeyboardButton("⤾ Back", callback_data='back')]]
    reply_markup = InlineKeyboardMarkup(help_keyboard)

    await context.bot.edit_message_caption(
        chat_id=update.effective_chat.id,
        message_id=update.callback_query.message.message_id,
        caption=help_text,
        reply_markup=reply_markup,
        parse_mode='markdown'
    )

# Register Handlers
application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
application.add_handler(CommandHandler('start', start, block=False))
