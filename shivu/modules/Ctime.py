from pymongo import ReturnDocument
from pyrogram.enums import ChatMemberStatus, ChatType
from shivu import user_totals_collection, shivuu
from pyrogram import Client, filters
from pyrogram.types import Message

ALLOWED_USER_ID = 7795212861

@shivuu.on_message(filters.command("ctime"))
async def change_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id != ALLOWED_USER_ID:
        await message.reply_text("You are not authorized to change the time.")
        return

    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text("This command can only be used in groups or supergroups.")
        return

    try:
        args = message.command
        if len(args) != 2:
            await message.reply_text('Please use: /changetime NUMBER')
            return

        new_frequency = int(args[1])
        if new_frequency < 1:
            await message.reply_text('The message frequency must be greater than or equal to 70.')
            return

        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(chat_id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await message.reply_text(f'Successfully changed message frequency to {new_frequency}.')
    except ValueError:
        await message.reply_text('Please provide a valid number.')
    except Exception as e:
        await message.reply_text(f'Failed to change message frequency. Error: {str(e)}')

# Optional: Set up logging
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def log_command_usage(command: str, user_id: int, chat_id: int, success: bool, error: str = None):
    if success:
        logger.info(f"Command '{command}' used by user {user_id} in chat {chat_id} succeeded.")
    else:
        logger.error(f"Command '{command}' used by user {user_id} in chat {chat_id} failed. Error: {error}")

@shivuu.on_message(filters.command("changetime"))
async def change_time(client: Client, message: Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    if user_id != ALLOWED_USER_ID:
        await message.reply_text("You are not authorized to change the time.")
        return

    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply_text("This command can only be used in groups or supergroups.")
        return

    try:
        args = message.command
        if len(args) != 2:
            await message.reply_text('Please use: /changetime NUMBER')
            return

        new_frequency = int(args[1])
        if new_frequency < 5:
            await message.reply_text('The message frequency must be greater than or equal to 70.')
            return

        chat_frequency = await user_totals_collection.find_one_and_update(
            {'chat_id': str(chat_id)},
            {'$set': {'message_frequency': new_frequency}},
            upsert=True,
            return_document=ReturnDocument.AFTER
        )

        await message.reply_text(f'Successfully changed message frequency to {new_frequency}.')
        await log_command_usage("/changetime", user_id, chat_id, True)
    except ValueError:
        await message.reply_text('Please provide a valid number.')
        await log_command_usage("/changetime", user_id, chat_id, False, "Invalid number format")
    except Exception as e:
        await message.reply_text(f'Failed to change message frequency. Error: {str(e)}')
        await log_command_usage("/changetime", user_id, chat_id, False, str(e))
      
