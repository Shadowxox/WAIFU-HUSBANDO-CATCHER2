import asyncio
import logging
from datetime import datetime, timedelta
from pyrogram import Client, filters, types as t
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from shivu import shivuu as bot, user_collection, collection, PARTNER

# Constants
DEVS = (7378476666)
CHAT_ID = "-1002337505439"
JOIN_URL = "https://t.me/The_Mugiwara_Support"
CHARACTERS_PER_PAGE = 10

# Lock dictionary to track command processing
claim_lock = {}

# New emoji list for fun responses
EMOJIOS = [
    "🌟", "🎉", "✨", "🌈", "💖", "🎀", "🍀", "🎊", 
    "🌸", "💫", "🔥", "🌌", "🐾", "🍭", "🎇", "🔔", 
    "🦋", "🌼", "🥳", "🦄"
]

async def format_time_delta(delta):
    seconds = delta.total_seconds()
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours)}h {int(minutes)}m {int(seconds)}s"

async def get_unique_characters(user_id, target_rarities=['⚪️ Common', '🟣 Rare', '🟡 Legendary', '🟢 Medium', '💮 Special Edition', '🔮 Limited Edition']):
    try:
        user_data = await user_collection.find_one({'id': user_id}, {'characters': 1})
        user_character_ids = {char['id'] for char in user_data['characters']} if user_data else set()

        pipeline = [
            {'$match': {'rarity': {'$in': target_rarities}, 'id': {'$nin': list(user_character_ids)}}},
            {'$sample': {'size': 1}}
        ]

        cursor = collection.aggregate(pipeline)
        characters = await cursor.to_list(length=None)
        return characters
    except Exception as e:
        logging.error(f"Error fetching unique characters: {e}")
        return []

@bot.on_message(filters.command(["cclaim"]))
async def hclaim(_, message: t.Message):
    user_id = message.from_user.id
    mention = message.from_user.mention

    if message.forward_date:
        return

    if user_id in claim_lock:
        await message.reply_text("Your claim request is already being processed. Please wait.")
        return

    claim_lock[user_id] = True  # Set the lock

    try:
        # Removed ban_collection checks
        if str(message.chat.id) != CHAT_ID:
            join_button = InlineKeyboardMarkup([[InlineKeyboardButton("Join Here", url=JOIN_URL)]])
            return await message.reply_text("Join to claim your daily free waifu...", reply_markup=join_button)

        user_data = await user_collection.find_one({'id': user_id}) or {
            'id': user_id,
            'username': message.from_user.username,
            'characters': [],
            'last_daily_reward': None
        }

        last_claimed_date = user_data.get('last_daily_reward')

        if last_claimed_date:
            last_claimed_date = last_claimed_date.replace(tzinfo=None)
            if last_claimed_date.date() == datetime.utcnow().date():
                remaining_time = timedelta(days=1) - (datetime.utcnow() - last_claimed_date)
                formatted_time = await format_time_delta(remaining_time)
                await message.reply_text(f"⏳ You've already claimed today! Next reward in: `{formatted_time}`")
                return

        unique_characters = await get_unique_characters(user_id)

        if not unique_characters:
            return await message.reply_text("🚫 No unique characters found.")

        await user_collection.update_one(
            {'id': user_id},
            {
                '$push': {'characters': {'$each': unique_characters}},
                '$set': {'last_daily_reward': datetime.utcnow()}
            }
        )

        for character in unique_characters:
            await message.reply_photo(photo=character['img_url'], caption=f"🎉 Congratulations {mention}! 🌟\n✨ ***Name***: {character['name']}\n🧬 ***Rarity***: {character['rarity']}\n📺 ***Anime***: {character['anime']}\n🍀 ***Come back tomorrow for another claim!***")

    except Exception as e:
        logging.error(f"Error in hclaim: {e}")
        await message.reply_text("An error occurred while processing your claim. Please try again later.")
    finally:
        claim_lock.pop(user_id, None)

@bot.on_message(filters.command(["check"]))
async def hfind(_, message: t.Message):
    if len(message.command) < 2:
        return await message.reply_text("📌 Please provide the ID 🆔", quote=True)

    waifu_id = message.command[1]
    waifu = await collection.find_one({'id': waifu_id})

    if not waifu:
        return await message.reply_text("🔍 No character found with that ID ❌", quote=True)

    top_users = await user_collection.aggregate([
        {'$match': {'characters.id': waifu_id}},
        {'$unwind': '$characters'},
        {'$match': {'characters.id': waifu_id}},
        {'$group': {'_id': '$id', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}},
        {'$limit': 5}
    ]).to_list(length=5)

    usernames = []
    for user_info in top_users:
        user_id = user_info['_id']
        try:
            user = await bot.get_users(user_id)
            usernames.append(user.username if user.username else f"➥ {user_id}")
        except Exception:
            usernames.append(f"➥ {user_id}")

    caption = (
        f"📜 ***Character Info***\n"
        f"🧩 ***Name***: {waifu['name']}\n"
        f"🧬 ***Rarity***: {waifu['rarity']}\n"
        f"📺 ***Anime***: {waifu['anime']}\n"
        f"🆔 ***ID***: {waifu['id']}\n\n"
        f"🏆 ***Top Collectors***:\n\n"
    )
    for i, user_info in enumerate(top_users):
        count = user_info['count']
        username = usernames[i]
        caption += f"{i + 1}. {username} x{count}\n"

    await message.reply_photo(photo=waifu['img_url'], caption=caption)

@bot.on_message(filters.command(["find"]))
async def cfind(_, message: t.Message):
    if len(message.command) < 2:
        return await message.reply_text("Please provide the anime name.", quote=True)

    anime_name = " ".join(message.command[1:])
    characters = await collection.find({'anime': anime_name}).to_list(length=None)

    if not characters:
        return await message.reply_text(f"No characters found from the anime {anime_name}.", quote=True)

    page = 0
    await send_character_page(message, characters, anime_name, page)

async def send_character_page(message, characters, anime_name, page):
    start = page * CHARACTERS_PER_PAGE
    end = start + CHARACTERS_PER_PAGE
    paginated_characters = characters[start:end]

    captions = [
        f"🎏 ***Name***: {char['name']}\n🪅 ***ID***: {char['id']}\n🧩 ***Rarity***: {char['rarity']} \n"
        for char in paginated_characters
    ]
    response = "\n".join(captions)

    keyboard = []
    if end < len(characters):
        keyboard.append([InlineKeyboardButton("Next", callback_data=f"next_{anime_name}_{page+1}")])

    await message.reply_text(
        f"🍁 Characters from {anime_name} (Page {page + 1}):\n\n{response}",
        reply_markup=InlineKeyboardMarkup(keyboard) if keyboard else None,
        quote=True
    )

@bot.on_callback_query(filters.regex(r"next_(.+)_(\d+)"))
async def next_page_callback(_, callback_query: t.CallbackQuery):
    anime_name, page = callback_query.data.split("_")[1], int(callback_query.data.split("_")[2])
    characters = await collection.find({'anime': anime_name}).to_list(length=None)
    await send_character_page(callback_query.message, characters, anime_name, page)
    await callback_query.answer()
