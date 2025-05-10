import os
import requests
from io import BytesIO
from pymongo import ReturnDocument
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from gridfs import GridFS
from shivu import application, sudo_users, CHARA_CHANNEL_ID, collection, user_collection,shivuu
from pyrogram import filters
from shivu import shivuu, collection
from pyrogram.types import InputMediaPhoto
import os

# Define the wrong format message and rarity map
WRONG_FORMAT_TEXT = """Wrong ❌ format... eg. /upload reply to photo muzan-kibutsuji Demon-slayer 3

Format: /upload reply character-name anime-name rarity-number

Use rarity number according to the rarity map.

rarity_map = {
    1: "⚪️ Common",
    2: "🟣 Rare",
    3: "🟡 Legendary",
    4: "🟢 Medium",
    5: "💮 Special Edition",
    6: "🔮 Limited Edition",
    7: "🎐 Celestial",
    8: "🔞 Erotic",
    9: "💝 Valentine Special",
    10: "🧬 X Verse",
    11: "🎃 Halloween Special",
    12: "❄️ Winter Special",
    13: "🌤️ Summer Special",
    14: "💫 Angelic"
}
"""

# Define the channel ID and rarity map
CHARA_CHANNEL_ID = -1002621413939

rarity_map = {
    1: "⚪️ Common",
    2: "🟣 Rare",
    3: "🟡 Legendary",
    4: "🟢 Medium",
    5: "💮 Special Edition",
    6: "🔮 Limited Edition",
    7: "🎐 Celestial",
    8: "🔞 Erotic",
    9: "💝 Valentine Special",
    10: "🧬 X Verse",
    11: "🎃 Halloween Special",
    12: "❄️ Winter Special",
    13: "🌤️ Summer Special",
    14: "💫 Angelic"
}

# Function to find the next available ID for a character
async def find_available_id():
    cursor = collection.find().sort('id', 1)
    ids = [doc['id'] for doc in await cursor.to_list(length=None) if 'id' in doc]
    return str(max(map(int, ids)) + 1).zfill(2) if ids else '01'

# Function to upload file to Catbox
def upload_to_catbox(file_path):
    url = "https://catbox.moe/user/api.php"
    with open(file_path, "rb") as file:
        response = requests.post(
            url,
            data={"reqtype": "fileupload"},
            files={"fileToUpload": file}
        )
        if response.status_code == 200 and response.text.startswith("https"):
            return response.text
        else:
            raise Exception(f"Error uploading to Catbox: {response.text}")

# List of allowed user IDs
allowed_users = [
    7795212861, 5758240622, 7361967332
]

@shivuu.on_message(filters.command(["upload"]) & filters.user(allowed_users))
async def upload_character(client, message):
    reply = message.reply_to_message
    if reply and (reply.photo or reply.document):
        args = message.text.split()
        if len(args) != 4:
            await client.send_message(chat_id=message.chat.id, text=WRONG_FORMAT_TEXT)
            return

        # Extract character details from the command arguments
        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()
        rarity = int(args[3])

        # Validate rarity value
        if rarity not in rarity_map:
            await message.reply_text("Invalid rarity value. Please use a value between 1 and 13.")
            return

        rarity_text = rarity_map[rarity]
        available_id = await find_available_id()

        # Prepare character data
        character = {
            'name': character_name,
            'anime': anime,
            'rarity': rarity_text,
            'id': available_id
        }

        processing_message = await message.reply("<ᴘʀᴏᴄᴇꜱꜱɪɴɢ>....")
        path = await reply.download()
        try:
            # Upload image to Catbox
            catbox_url = upload_to_catbox(path)
            character['img_url'] = catbox_url

            # Send character details to the channel
            await client.send_photo(
                chat_id=CHARA_CHANNEL_ID,
                photo=catbox_url,
                caption=(
                    f"Character Name: {character_name}\n"
                    f"Anime Name: {anime}\n"
                    f"Rarity: {rarity_text}\n"
                    f"ID: {available_id}\n"
                    f"Added by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                ),

            )

            # Insert character into the database
            await collection.insert_one(character)
            await message.reply_text('CHARACTER ADDED....')
        except Exception as e:
            await message.reply_text(f"Character Upload Unsuccessful. Error: {str(e)}")
        finally:
            os.remove(path)  # Clean up the downloaded file
    else:
        await message.reply_text("Please reply to a photo or document.")



async def delete_character(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Ask my Owner to use this Command...')
        return

    try:
        if len(context.args) != 1:
            await update.message.reply_text('Incorrect format... Please use: /delete ID')
            return

        character = await collection.find_one_and_delete({'id': context.args[0]})
        if character:
            await update.message.reply_text('Character deleted successfully.')
        else:
            await update.message.reply_text('Character not found in the database.')
    except Exception as e:
        await update.message.reply_text(f'Error occurred: {str(e)}')












async def updates(update: Update, context: CallbackContext) -> None:
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('You do not have permission to use this command.')
        return

    try:
        args = context.args
        if len(args) != 3:
            await update.message.reply_text('Incorrect format. Please use: /update_character_all id field new_value')
            return

        # Extract arguments
        character_id = args[0]
        field = args[1]
        new_value = args[2]

        # Check if the field is valid
        valid_fields = ['img_url', 'name', 'anime', 'rarity']
        if field not in valid_fields:
            await update.message.reply_text(f'Invalid field. Please use one of the following: {", ".join(valid_fields)}')
            return

        # Adjust value formatting
        if field in ['name', 'anime']:
            new_value = new_value.replace('-', ' ').title()
        elif field == 'rarity':
            rarity_map = {
                1: "⚪️ Common",
                2: "🟣 Rare",
                3: "🟡 Legendary",
                4: "🟢 Medium",
                5: "💮 Special Edition",
                6: "🔮 Limited Edition",
                7: "🎐 Celestial",
                8: "🔞 Erotic",
                9: "💝 Valentine Special",
                10: "🧬 X Verse",
                11: "🎃 Halloween Special",
                12: "❄️ Winter Special",
                13: "🌤️ Summer Special",
                14: "💫 Angelic"
            }
            try:
                new_value = rarity_map[int(new_value)]
            except (ValueError, KeyError):
                await update.message.reply_text('Invalid rarity. Please provide a valid rarity number.')
                return

        # Update the character in `collection`
        collection_result = await collection.update_many(
            {"characters.id": character_id},
            {"$set": {f"characters.$[elem].{field}": new_value}},
            array_filters=[{"elem.id": character_id}]
        )

        # Update the character in `user_collection`
        user_result = await user_collection.update_many(
            {"characters.id": character_id},
            {"$set": {f"characters.$[elem].{field}": new_value}},
            array_filters=[{"elem.id": character_id}]
        )

        total_modified = collection_result.modified_count + user_result.modified_count

        if total_modified == 0:
            await update.message.reply_text("Character not found in any collection.")
        else:
            await update.message.reply_text(f"Character updated successfully in {total_modified} documents across all collections.")

    except Exception as e:
        await update.message.reply_text(f"An error occurred: {str(e)}")


UPDATES_HANDLER = CommandHandler('update', updates, block=False)
application.add_handler(UPDATES_HANDLER)


application.add_handler(CommandHandler('delete', delete_character, block=False))

