from telethon.tl.types import MessageMediaPhoto
from telethon.errors import FloodWaitError
from pyrogram import filters
from pyrogram.types import Message
from shivu import app, shivuu, collection, OWNER_ID, PARTNER
import asyncio

CHANNEL = "database_shadowtestingbot"
ALLOWED_USERS = [OWNER_ID] + PARTNER  # Only allowed users can trigger the sync


@shivuu.on_message(filters.command("fetchwaifus") & filters.user(ALLOWED_USERS))
async def fetch_waifus_command(_, message: Message):
    await message.reply_text("📥 Fetching waifus from the database channel...")

    total = 0
    success = 0
    fail = 0

    try:
        async for msg in app.iter_messages(CHANNEL):
            total += 1

            if not msg.photo and not isinstance(msg.media, MessageMediaPhoto):
                continue
            if not msg.text:
                continue

            text = msg.text.strip()
            lines = text.split("\n")

            name = lines[0].strip() if lines else "Unknown"
            waifu_id = None

            for line in lines:
                if "ID:" in line:
                    try:
                        waifu_id = int(line.split("ID:")[-1].strip())
                    except ValueError:
                        continue

            if not waifu_id:
                fail += 1
                continue

            file_id = msg.photo.file_id if hasattr(msg.photo, 'file_id') else None
            if not file_id:
                fail += 1
                continue

            await collection.update_one(
                {"id": waifu_id},
                {"$set": {
                    "id": waifu_id,
                    "file_id": file_id,
                    "img_url": file_id,
                    "name": name
                }},
                upsert=True
            )
            success += 1

    except FloodWaitError as e:
        await message.reply_text(f"⏳ Flood wait! Please wait {e.seconds} seconds.")
        return
    except Exception as e:
        await message.reply_text(f"❌ Unexpected error: {e}")
        return

    await message.reply_text(
        f"✅ Waifu sync complete!\n"
        f"📄 Total messages scanned: `{total}`\n"
        f"✅ Inserted/Updated: `{success}`\n"
        f"❌ Skipped/Failed: `{fail}`"
    )
