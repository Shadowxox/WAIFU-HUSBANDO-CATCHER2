import random
from html import escape
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import CallbackContext, CallbackQueryHandler, CommandHandler
from datetime import datetime, timedelta

from shivu import application, SUPPORT_CHAT, UPDATE_CHAT, BOT_USERNAME, db, GROUP_ID
from shivu import pm_users as collection

# Record the bot start time
bot_start_time = datetime.now()

# Add your image URLs here
PHOTO_URLS = [
    "https://files.catbox.moe/7vr2im.jpg",
]

def get_random_photo_url():
    return random.choice(PHOTO_URLS)

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
    caption = """

    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫   
      ✾ Wᴇʟᴄᴏᴍɪɴɢ ʏᴏᴜ ᴛᴏ ᴛʜᴇ Waifu Catcher Bᴏᴛ   
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
    ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
    ┠ ➻  I ᴡɪʟʟ Hᴇʟᴘ Yᴏᴜ Fɪɴᴅ Yᴏᴜʀ Waifu Hᴜsʙᴀɴᴅᴏ
    ┃        ɪɴ Yᴏᴜʀ Gʀᴏᴜᴘ Cʜᴀᴛ. 
    ┠ ➻  Yᴏᴜ ᴄᴀɴ sᴇᴀʟ ᴛʜᴇᴍ ʙʏ /guess ᴄᴏᴍᴍᴀɴᴅ 
    ┃         ᴀɴᴅ ᴀᴅᴅ ᴛᴏ ʏᴏᴜʀ ʜᴀʀᴇᴍ.
    ┗━━━━━━━━━━━━━━━━━━━━━━━━━━━⧫
      Tᴀᴘ ᴏɴ "Hᴇʟᴘ" ғᴏʀ ᴍᴏʀᴇ ᴄᴏᴍᴍᴀɴᴅs.
    """
    keyboard = [
        [InlineKeyboardButton("ADD ME", url=f'http://t.me/Catch_your_harem_bot?startgroup=new')],
        [InlineKeyboardButton("SUPPORT", url=f'https://t.me/The_Mugiwara_Support'), InlineKeyboardButton("UPDATES", url=f'https://t.me/psupport_harem_botchat')],
        [InlineKeyboardButton("HELP", callback_data='help')],
        [InlineKeyboardButton("DEVELOPER", url=f'https://t.me/Silent_zoro')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    photo_url = get_random_photo_url()

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup, parse_mode='markdown')

async def send_group_message(update: Update, context: CallbackContext) -> None:
    # Calculate uptime
    current_time = datetime.now()
    uptime = current_time - bot_start_time
    uptime_str = str(timedelta(seconds=int(uptime.total_seconds())))

    caption = f"""
    🎴Alive!?... Connect to me in PM for more information.

    Bot Uptime: {uptime_str}
    """
    keyboard = [
        [InlineKeyboardButton("ADD ME", url=f'http://t.me/waifuteam_bot?startgroup=new')],
        [InlineKeyboardButton("SUPPORT", url=f'https://t.me/team_jjk'), InlineKeyboardButton("UPDATES", url=f'https://t.me/team_network_jjk')],
        [InlineKeyboardButton("HELP", callback_data='help')],
        [InlineKeyboardButton("DEVELOPER", url=f'https://t.me/soham_6540')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    photo_url = get_random_photo_url()

    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url, caption=caption, reply_markup=reply_markup)

async def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await send_help_message(update, context)
    elif query.data == 'back':
        await send_private_message(update, context)

async def send_help_message(update: Update, context: CallbackContext) -> None:
    help_text = """
    ***Help Section:***

    ***/guess: To guess character (only works in group)***
    ***/fav: Add your favorite***
    ***/trade: To trade characters***
    ***/gift: Give any character from your collection to another user (only works in groups)***
    ***/collection: To see your collection***
    ***/topgroups: See top groups where people guess the most***
    ***/top: See top users***
    ***/ctop: Your chat top***
    ***/changetime: Change character appear time (only works in groups)***
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

application.add_handler(CallbackQueryHandler(button, pattern='^help$|^back$', block=False))
start_handler = CommandHandler('start', start, block=False)
application.add_handler(start_handler)
