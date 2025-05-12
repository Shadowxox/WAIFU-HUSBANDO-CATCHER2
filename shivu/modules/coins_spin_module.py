import asyncio
from datetime import datetime
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from motor.motor_asyncio import AsyncIOMotorClient

# --- Configuration ---
MONGO_URL = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net/"  # Replace this
mongo_client = AsyncIOMotorClient(MONGO_URL)
users_collection = mongo_client['Character_catcher']['users']

SHOP_COSTS = {
    "🕱 Rare": 500,
    "🌀 Medium": 1000,
    "🦤 Legendary": 5000,
    "🚾 Special Edition": 10000,
    "🔮 Limited Edition": 20000,
    "🌐 Celestial": 25000,
    "🎭 X Verse": 35000,
    "🔞 Erotic": 80000,
    "💖 Valentine Special": 45000,
    "❄️ Winter Special": 48000,
    "🌤️ Summer Special": 50000,
    "🎃 Halloween Special": 46000,
    "🎴 AMV": 145000,
    "🎥 Hollywood": 150000
}

DAILY_REWARD = 100
WEEKLY_REWARD = 1000
GROUPS_TO_AUTO_DELETE = [-1002264558318, -1002643948280]

# --- Helper ---
async def get_user(user_id):
    user = await users_collection.find_one({"user_id": user_id})
    if not user:
        new_user = {"user_id": user_id, "coins": 0, "favorites": [], "daily_claimed": None, "weekly_claimed": None}
        await users_collection.insert_one(new_user)
        return new_user
    return user

# --- /shop ---
@Client.on_message(filters.command("shop"))
async def shop_handler(c, m: Message):
    text = (
        "🌟 *Welcome to the Rarity Shop!* 🌟\n\n"
        "Here, you can spin for characters of different rarities. Each rarity has its own unique characters and spin cost.\n\n"
        "*Please choose the rarity you want to spin for:*"
    )

    buttons, row = [], []
    for idx, rarity in enumerate(SHOP_COSTS, 1):
        row.append(InlineKeyboardButton(text=rarity, callback_data=f"spin_{rarity}"))
        if idx % 3 == 0:
            buttons.append(row)
            row = []
    if row:
        buttons.append(row)

    await m.reply(text, reply_markup=InlineKeyboardMarkup(buttons), parse_mode="Markdown")

# --- Callback for spin buttons ---
@Client.on_callback_query(filters.regex(r"^spin_"))
async def handle_spin_button(c, cb: CallbackQuery):
    rarity = cb.data.split("spin_")[1]
    cost = SHOP_COSTS.get(rarity)

    user = await get_user(cb.from_user.id)
    if user["coins"] < cost:
        await cb.answer("❌ Not enough coins!", show_alert=True)
        return

    await users_collection.update_one({"user_id": cb.from_user.id}, {"$inc": {"coins": -cost}})
    await cb.message.reply(f"🌰 You spun for {rarity} rarity by spending {cost} coins!\n🔄 [Character reward coming soon...]")
    await cb.answer()

# --- /daily ---
@Client.on_message(filters.command("daily"))
async def daily_handler(c, m: Message):
    user = await get_user(m.from_user.id)
    now = datetime.utcnow()

    last_claim = user.get("daily_claimed")
    if last_claim and (now - last_claim).total_seconds() < 86400:
        return await m.reply("🕒 You've already claimed your daily reward today.")

    await users_collection.update_one(
        {"user_id": m.from_user.id},
        {"$set": {"daily_claimed": now}, "$inc": {"coins": DAILY_REWARD}}
    )
    await m.reply(f"🏷️ You received your daily reward of {DAILY_REWARD} coins!")

# --- /weekly ---
@Client.on_message(filters.command("weekly"))
async def weekly_handler(c, m: Message):
    user = await get_user(m.from_user.id)
    now = datetime.utcnow()

    last_claim = user.get("weekly_claimed")
    if last_claim and (now - last_claim).total_seconds() < 604800:
        return await m.reply("🕒 You've already claimed your weekly reward. Try again next week!")

    await users_collection.update_one(
        {"user_id": m.from_user.id},
        {"$set": {"weekly_claimed": now}, "$inc": {"coins": WEEKLY_REWARD}}
    )
    await m.reply(f"🎉 You received your weekly reward of {WEEKLY_REWARD} coins!")

# --- /profile ---
@Client.on_message(filters.command("profile"))
async def profile_handler(c, m: Message):
    user = await get_user(m.from_user.id)
    coins = user.get("coins", 0)
    favorites = user.get("favorites", [])

    favs_text = "\n".join([f"- {f}" for f in favorites]) if favorites else "No favorite waifus added yet."
    profile_text = (
        f"👤 *User Profile*\n"
        f"🪙 Coins: `{coins}`\n\n"
        f"❤️ *Favorite Waifus:*\n{favs_text}"
    )

    msg = await m.reply(profile_text, parse_mode="Markdown")
    if m.chat.id in GROUPS_TO_AUTO_DELETE:
        await asyncio.sleep(30)
        await msg.delete()
        await m.delete()
