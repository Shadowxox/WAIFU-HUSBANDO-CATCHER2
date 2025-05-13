from pyrogram import filters
from pyrogram.types import Message
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from telethon.errors import FloodWaitError
from shivu import app, shivuu, collection

CHANNEL = "database_shadowtestingbot"
ALLOWED_USERS = "5758240622, 7795212861, 7361967332"  # ✅ ONLY partners, not owner


@shivuu.on_message(filters.command("fetchwaifus"))
async def fetch_waifus_command(_, message: Message):
    user_id = message.from_user.id
    if user_id not in ALLOWED_USERS:
        return await message.reply_text("🚫 Only bot partners can use this command.")

    await message.reply_text("📥 Fetching waifus from the database channel...")

    total = success = fail = 0

    try:
        async for msg in app.iter_messages(CHANNEL):
            total += 1
            text = msg.text or ""
            lines = text.strip().split("\n")
            name = lines[0].strip() if lines else "Unknown"

            waifu_id = None
            anime = "Unknown"
            rarity = "Unknown"

            for line in lines:
                if "ID:" in line:
                    try:
                        waifu_id = int(line.split("ID:")[-1].strip())
                    except:
                        pass
                elif "Anime:" in line:
                    anime = line.split("Anime:")[-1].strip()
                elif "Rarity:" in line:
                    rarity = line.split("Rarity:")[-1].strip()

            if not waifu_id:
                fail += 1
                continue

            file_id = None
            field_type = None

            if msg.photo and hasattr(msg.photo, "file_id"):
                file_id = msg.photo.file_id
                field_type = "img_url"
            elif msg.video and hasattr(msg.video, "file_id"):
                file_id = msg.video.file_id
                field_type = "vid_url"

            if not file_id or not field_type:
                fail += 1
                continue

            await collection.update_one(
                {"id": waifu_id},
                {"$set": {
                    "id": waifu_id,
                    "name": name,
                    "anime": anime,
                    "rarity": rarity,
                    field_type: file_id,
                    "file_id": file_id  # fallback/common
                }},
                upsert=True
            )
            success += 1

    except FloodWaitError as e:
        return await message.reply_text(f"⏳ Flood wait! Please wait {e.seconds} seconds.")
    except Exception as e:
        return await message.reply_text(f"❌ Error: {e}")

    await message.reply_text(
        f"✅ Sync complete!\n"
        f"📄 Total messages checked: `{total}`\n"
        f"✅ Inserted/Updated: `{success}`\n"
        f"❌ Failed to process: `{fail}`"
    )
