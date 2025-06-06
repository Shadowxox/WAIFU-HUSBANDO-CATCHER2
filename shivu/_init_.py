import logging  
import os
from pyrogram import Client 
from telegram.ext import Application
from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from telethon import events, Button
from telethon.sync import TelegramClient

# Setup logging
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    handlers=[logging.FileHandler("log.txt"), logging.StreamHandler()],
    level=logging.INFO,
)

logging.getLogger("apscheduler").setLevel(logging.ERROR)
logging.getLogger('httpx').setLevel(logging.WARNING)
logging.getLogger("pyrate_limiter").setLevel(logging.ERROR)
LOGGER = logging.getLogger(__name__)

# Load config
from shivu.config import Development as Config

api_id = Config.api_id
api_hash = Config.api_hash
TOKEN = Config.TOKEN
GROUP_ID = Config.GROUP_ID
CHARA_CHANNEL_ID = Config.CHARA_CHANNEL_ID 
mongo_url = Config.mongo_url 
PHOTO_URL = Config.PHOTO_URL 
SUPPORT_CHAT = Config.SUPPORT_CHAT 
UPDATE_CHAT = Config.UPDATE_CHAT
BOT_USERNAME = Config.BOT_USERNAME 
sudo_users = Config.sudo_users
OWNER_ID = Config.OWNER_ID 
PARTNER = Config.PARTNER

# Initialize bots and database
application = Application.builder().token(TOKEN).build()
shivuu = Client("Shivu", api_id, api_hash, bot_token=TOKEN)
app = TelegramClient('bot', api_id, api_hash).start(bot_token=TOKEN)

lol = AsyncIOMotorClient(mongo_url)
db = lol['Character_catcher']
collection = db['anime_characters_lol']
waifu_collection = collection
user_totals_collection = db['user_totals_lmaoooo']
user_collection = db["user_collection_lmaoooo"]
group_user_totals_collection = db['group_user_totallllllsssssss']
top_global_groups_collection = db['top_global_groups']
pm_users = db['total_pm_users']
users_collection = db['users']
prizes_collection = db['prizes']
shops_collection = db['shops']
ban_collection = db['bans']
banned_collection = db['bannedcollecion']

# ✅ Dynamic module loader
ALL_MODULES = [
    f.replace(".py", "") for f in os.listdir(os.path.dirname(__file__))
    if f.endswith(".py") and f != "__init__.py"
]

for module in ALL_MODULES:
    try:
        imported_module = __import__(f"shivu.modules.{module}")
        LOGGER.info(f"Imported module: {module}")
    except Exception as e:
        LOGGER.error(f"Failed to import module {module}: {e}")
