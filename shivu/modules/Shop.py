from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery, Message
from motor.motor_asyncio import AsyncIOMotorClient

# MongoDB setup
MONGO_URL = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net/"
mongo_client = AsyncIOMotorClient(MONGO_URL)
db = mongo_client['Character_catcher']
shop_collection = db['shop_items']
users_collection = db['users']
collection_collection = db['user_collection_lmaoooo']

# Partner-only access
PARTNER_IDS = ["7361967332", "7795212861", "5758240622"]

# Pagination config
WAIFUS_PER_PAGE = 1


# /addshop command
@Client.on_message(filters.command("addshop") & filters.user(PARTNER_IDS))
async def add_waifu_to_shop(client, message: Message):
    try:
        if len(message.command) != 4:
            await message.reply("❌ Usage: /addshop {waifu_id} {price} {quantity}")
            return

        _, waifu_id, price, quantity = message.text.split()
        price = int(price)
        quantity = int(quantity)

        waifu = await collection_collection.find_one({"id": int(waifu_id)})
        if not waifu:
            await message.reply("❌ Waifu not found.")
            return

        image = waifu.get("file_id")
        if not image:
            await message.reply("❌ Waifu image not found.")
            return

        await shop_collection.update_one(
            {"waifu_id": waifu_id},
            {"$set": {
                "waifu_id": waifu_id,
                "price": price,
                "quantity": quantity,
                "image": image,
                "name": waifu.get("name"),
                "anime": waifu.get("anime"),
                "rarity": waifu.get("rarity")
            }},
            upsert=True
        )
        await message.reply(
            f"✅ Waifu ID `{waifu_id}` added to shop for `{price}` coins "
            f"with `{quantity}` in stock."
        )
    except Exception as e:
        await message.reply(f"❌ Error: {e}")

# /rshop command
@Client.on_message(filters.command("rshop") & filters.user(PARTNER_IDS))
async def remove_waifu_from_shop(client, message: Message):
    try:
        if len(message.command) != 2:
            await message.reply("❌ Usage: /rshop {waifu_id}")
            return

        waifu_id = message.command[1]
        result = await shop_collection.delete_one({"waifu_id": waifu_id})

        if result.deleted_count == 0:
            await message.reply("❌ Waifu not found in the shop.")
        else:
            await message.reply(f"✅ Waifu ID {waifu_id} removed from the shop.")
    except Exception as e:
        await message.reply(f"❌ Error: {e}")


# /shop command
@Client.on_message(filters.command("shop"))
async def shop_view(client, message: Message):
    await send_shop_page(client, message.chat.id, 0)


# Shop display page
async def send_shop_page(client, chat_id, page):
    skip = page * WAIFUS_PER_PAGE
    waifus = await shop_collection.find().skip(skip).limit(WAIFUS_PER_PAGE).to_list(length=WAIFUS_PER_PAGE)
    total = await shop_collection.count_documents({})

    if not waifus:
        await client.send_message(chat_id, "❌ No waifus in the shop.")
        return

    waifu = waifus[0]
    text = (
        f"🆔 ID: `{waifu['waifu_id']}`\n"
        f"👤 Name: {waifu.get('name', 'Unknown')}\n"
        f"📺 Anime: {waifu.get('anime', 'Unknown')}\n"
        f"💎 Rarity: {waifu.get('rarity', 'N/A')}\n"
        f"💰 Price: `{waifu['price']}` coins"
    )

    buttons = [
        [InlineKeyboardButton("🛒 Buy", callback_data=f"buy:{waifu['waifu_id']}")],
        [
            InlineKeyboardButton("⬅️ Previous", callback_data=f"shop:{page-1}") if page > 0 else None,
            InlineKeyboardButton("➡️ Next", callback_data=f"shop:{page+1}") if skip + WAIFUS_PER_PAGE < total else None
        ],
        [InlineKeyboardButton("❌ Close", callback_data="close")]
    ]
    markup = InlineKeyboardMarkup([row for row in buttons if any(row)])
    await client.send_photo(chat_id, photo=waifu['image'], caption=text, reply_markup=markup)


# Pagination callback
@Client.on_callback_query(filters.regex("^shop:(-?\d+)$"))
async def paginate_shop(client, callback_query: CallbackQuery):
    page = int(callback_query.data.split(":")[1])
    await callback_query.message.delete()
    await send_shop_page(client, callback_query.message.chat.id, page)


# Buy handler
@Client.on_callback_query(filters.regex("^buy:(\d+)$"))
async def buy_waifu(client, callback_query: CallbackQuery):
    waifu_id = callback_query.data.split(":")[1]
    user_id = callback_query.from_user.id
    waifu = await shop_collection.find_one({"waifu_id": waifu_id})

    if not waifu:
        await callback_query.answer("❌ Waifu not found.", show_alert=True)
        return

    user = await users_collection.find_one({"user_id": user_id})
    if not user or user.get("coins", 0) < waifu["price"]:
        await callback_query.answer("❌ Not enough coins.", show_alert=True)
        return

    await users_collection.update_one({"user_id": user_id}, {"$inc": {"coins": -waifu["price"]}})
    await collection_collection.update_one(
        {"user_id": user_id, "id": int(waifu_id)},
        {"$inc": {"count": 1}},
        upsert=True
    )

    await callback_query.answer("✅ Waifu purchased!")
    await callback_query.message.delete()


# Close button handler
@Client.on_callback_query(filters.regex("^close$"))
async def close_shop(client, callback_query: CallbackQuery):
    await callback_query.message.delete()


# /shoplist command
@Client.on_message(filters.command("shoplist") & filters.user(PARTNER_IDS))
async def list_shop_items(client, message: Message):
    waifus = await shop_collection.find().to_list(length=100)
    if not waifus:
        await message.reply("🛒 The shop is empty.")
        return

    lines = [f"🛒 **Shop Waifus ({len(waifus)})**:\n"]
    for waifu in waifus:
        lines.append(f"🆔 `{waifu['waifu_id']}` — 💰 {waifu['price']} coins")

    text = "\n".join(lines)
    await message.reply(text)
