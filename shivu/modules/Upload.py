import os
import requests
from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from pyrogram import filters
from shivu import shivuu, application, sudo_users, CHARA_CHANNEL_ID, collection, user_collection

# Use a separate collection to store reusable IDs
reuse_id_collection = collection.database['reuse_ids']

# Allowed users who can upload
allowed_users = [7795212861, 5758240622, 7361967332, 6484111272,
                 7133552331, 7812770062,
                ]

# Rarity map
rarity_map = {
    1: "🔱 Rare",
    2: "🌀 Medium",
    3: "🦄 Legendary",
    4: "💮 Special Edition",
    5: "🔮 Limited Edition",
    6: "🎐 Celestial",
    7: "🔞 Erotic",
    8: "💞 Valentine Special",
    9: "🎭 X Verse",
    10: "🎃 Halloween Special",
    11: "❄️ Winter Special",
    12: "🌤️ Summer Special",
    13: "🎴 AMV",
    14: "🎥 Hollywood"
}

# Error text
WRONG_FORMAT_TEXT = """Wrong ❌ format... eg. /upload reply to photo muzan-kibutsuji Demon-slayer 3

Format: /upload reply character-name anime-name rarity-number
"""

# Upload to catbox.moe

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
        raise Exception(f"Catbox upload failed: {response.text}")

# Get available ID (reuses deleted IDs if available)
async def find_available_id():
    reused = await reuse_id_collection.find_one_and_delete({})
    if reused:
        return reused['id']
    cursor = collection.find().sort('id', 1)
    ids = [int(doc['id']) for doc in await cursor.to_list(length=None) if 'id' in doc]
    return str(max(ids) + 1).zfill(2) if ids else '01'

# Upload handler
@shivuu.on_message(filters.command(["upload"]) & filters.user(allowed_users))
async def upload_character(client, message):
    reply = message.reply_to_message
    if reply and (reply.video or reply.photo or (reply.document and reply.document.mime_type.startswith("video/"))):
        args = message.text.split()
        if len(args) != 4:
            await message.reply_text(WRONG_FORMAT_TEXT)
            return

        character_name = args[1].replace('-', ' ').title()
        anime = args[2].replace('-', ' ').title()
        try:
            rarity = int(args[3])
            rarity_text = rarity_map[rarity]
        except:
            await message.reply("Invalid rarity number.")
            return

        character_id = await find_available_id()
        character = {
            'name': character_name,
            'anime': anime,
            'rarity': rarity_text,
            'id': character_id
        }

        processing = await message.reply("<Processing>...")
        path = await reply.download()
        try:
            catbox_url = upload_to_catbox(path)
            character['img_url'] = catbox_url

            if reply.video:
                await client.send_video(
                    chat_id=CHARA_CHANNEL_ID,
                    video=catbox_url,
                    caption=f"Character Name: {character_name}\nAnime: {anime}\nRarity: {rarity_text}\nID: {character_id}\nAdded by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                )
            else:
                await client.send_photo(
                    chat_id=CHARA_CHANNEL_ID,
                    photo=catbox_url,
                    caption=f"Character Name: {character_name}\nAnime: {anime}\nRarity: {rarity_text}\nID: {character_id}\nAdded by [{message.from_user.first_name}](tg://user?id={message.from_user.id})"
                )

            await collection.insert_one(character)
            await message.reply("Character added successfully.")
        except Exception as e:
            await message.reply(f"Upload failed: {e}")
        finally:
            os.remove(path)
    else:
        await message.reply("Reply to a photo, document, or video to upload.")

# Delete handler
async def delete_character(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Unauthorized.')
        return

    if len(context.args) != 1:
        await update.message.reply_text('Usage: /delete ID')
        return

    character_id = context.args[0]
    character = await collection.find_one_and_delete({'id': character_id})
    if character:
        await reuse_id_collection.insert_one({'id': character_id})
        await update.message.reply_text(f'Character {character_id} deleted and ID reused.')
    else:
        await update.message.reply_text('Character not found.')

# Update command
async def updates(update: Update, context: CallbackContext):
    if str(update.effective_user.id) not in sudo_users:
        await update.message.reply_text('Unauthorized.')
        return

    args = context.args
    if len(args) != 3:
        await update.message.reply_text('Usage: /update id field new_value')
        return

    character_id, field, new_value = args
    valid_fields = ['img_url', 'name', 'anime', 'rarity']
    if field not in valid_fields:
        await update.message.reply_text(f'Field must be one of: {", ".join(valid_fields)}')
        return

    if field in ['name', 'anime']:
        new_value = new_value.replace('-', ' ').title()
    elif field == 'rarity':
        try:
            new_value = rarity_map[int(new_value)]
        except:
            await update.message.reply_text('Invalid rarity number.')
            return

    try:
        result1 = await collection.update_many(
            {"id": character_id},
            {"$set": {field: new_value}}
        )
        result2 = await user_collection.update_many(
            {"characters.id": character_id},
            {"$set": {f"characters.$[elem].{field}": new_value}},
            array_filters=[{"elem.id": character_id}]
        )
        modified = result1.modified_count + result2.modified_count
        if modified:
            await update.message.reply_text(f"Updated {modified} documents.")
        else:
            await update.message.reply_text("Character not found.")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

# Add handlers
application.add_handler(CommandHandler('delete', delete_character, block=False))
application.add_handler(CommandHandler('update', updates, block=False))
