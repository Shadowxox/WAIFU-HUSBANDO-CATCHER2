from pyrogram import filters
from pyrogram.types import Message
from . import shivuu as app, collection, db, capsify

shop_collection = db.admin_shop  # new MongoDB collection for the shop
PARTNER_IDS = [7361967332, 7795212861, 5758240622]  # Replace with actual partner Telegram IDs


@app.on_message(filters.command("addshop") & filters.user(PARTNER_IDS))
async def addshop_handler(_, message: Message):
    if len(message.command) != 4:
        return await message.reply_text(capsify("Usage: /addshop {waifu_id} {price} {quantity}"))

    waifu_id, price, quantity = message.command[1:]
    price, quantity = int(price), int(quantity)

    waifu = await collection.find_one({"id": int(waifu_id)})
    if not waifu:
        return await message.reply_text(capsify("Waifu not found."))

    await shop_collection.update_one(
        {"waifu_id": waifu_id},
        {"$set": {
            "waifu_id": waifu_id,
            "price": price,
            "quantity": quantity,
            "img_url": waifu.get("img_url"),
            "name": waifu.get("name"),
            "anime": waifu.get("anime"),
            "rarity": waifu.get("rarity")
        }},
        upsert=True
    )
    await message.reply_text(capsify(f"✅ Added {waifu.get('name')} to shop for {price} coins with {quantity} in stock."))


@app.on_message(filters.command("rshop") & filters.user(PARTNER_IDS))
async def rshop_handler(_, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(capsify("Usage: /rshop {waifu_id}"))

    waifu_id = message.command[1]
    result = await shop_collection.delete_one({"waifu_id": waifu_id})

    if result.deleted_count:
        await message.reply_text(capsify(f"✅ Waifu ID {waifu_id} removed from shop."))
    else:
        await message.reply_text(capsify("❌ Waifu not found in shop."))


@app.on_message(filters.command("shoplist") & filters.user(PARTNER_IDS))
async def shoplist_handler(_, message: Message):
    waifus = await shop_collection.find().to_list(length=100)
    if not waifus:
        return await message.reply_text(capsify("🛒 The shop is currently empty."))

    lines = [f"🛒 **Shop Items ({len(waifus)})**:"]
    for waifu in waifus:
        lines.append(f"🆔 `{waifu['waifu_id']}` — 💰 {waifu['price']} — 📦 {waifu.get('quantity', 0)}")

    await message.reply_text("\n".join(lines))
