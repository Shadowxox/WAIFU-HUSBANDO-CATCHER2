from pyrogram import filters
from pyrogram.types import Message
from shivu import shivuu, collection, db

shop_collection = db.admin_shop
ALLOWED_USER_IDS = [5758240622, 7795212861, 7361967332]

DEFAULT_PRICE = 80000  # 💰 Change if needed
DEFAULT_QUANTITY = 1  # 📦 Change if needed

@shivuu.on_message(filters.command("syncshop"))
async def sync_shop_command(_, message: Message):
    user_id = message.from_user.id
    if user_id not in ALLOWED_USER_IDS:
        return await message.reply_text("🚫 Only authorized waifu partners can use this command.")

    await message.reply_text("🛍️ Syncing waifus from MongoDB to shop...")

    waifus = await collection.find({"file_id": {"$exists": True}}).to_list(length=1000)
    if not waifus:
        return await message.reply_text("❌ No waifus found in the database.")

    inserted = 0
    for waifu in waifus:
        waifu_id = waifu.get("id")
        file_id = waifu.get("file_id")
        if not waifu_id or not file_id:
            continue

        await shop_collection.update_one(
            {"waifu_id": str(waifu_id)},
            {"$set": {
                "waifu_id": str(waifu_id),
                "image": file_id,
                "price": DEFAULT_PRICE,
                "quantity": DEFAULT_QUANTITY,
                "name": waifu.get("name", "Unknown"),
                "anime": waifu.get("anime", "Unknown"),
                "rarity": waifu.get("rarity", "Unknown")
            }},
            upsert=True
        )
        inserted += 1

    await message.reply_text(
        f"✅ Shop sync complete!\n"
        f"📦 Waifus added/updated: `{inserted}`"
    )
