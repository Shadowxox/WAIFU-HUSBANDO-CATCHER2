# fetch_waifus_user.py

from telethon.sync import TelegramClient
from telethon.tl.types import MessageMediaPhoto, MessageMediaDocument
from pymongo import MongoClient

api_id = 23287799
api_hash = "9f4f17dae2181ee22c275b9b40a3c907"
mongo_url = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net"

client = TelegramClient("user", api_id, api_hash)
mongo = MongoClient(mongo_url)
db = mongo["Character_catcher"]
collection = db["anime_characters_lol"]

CHANNEL = "database_shadowtestingbot"

def extract_info(text):
    lines = text.strip().split("\n")
    name = lines[0].strip() if lines else "Unknown"
    waifu_id, anime, rarity = None, "Unknown", "Unknown"

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

    return name, waifu_id, anime, rarity


def main():
    client.start()
    print("🔍 Fetching waifus from channel...")

    total, success, fail = 0, 0, 0
    img_count = 0
    vid_count = 0

    for msg in client.iter_messages(CHANNEL):
        total += 1
        if not msg.text or (not msg.photo and not msg.video):
            continue

        name, waifu_id, anime, rarity = extract_info(msg.text)
        if not waifu_id:
            fail += 1
            continue

        field_type = None
        file_id = None

        if msg.photo:
            file_id = msg.photo.file_id
            field_type = "img_url"
            img_count += 1
        elif msg.video:
            file_id = msg.video.file_id
            field_type = "vid_url"
            vid_count += 1

        if not file_id or not field_type:
            fail += 1
            continue

        collection.update_one(
            {"id": waifu_id},
            {"$set": {
                "id": waifu_id,
                "name": name,
                "anime": anime,
                "rarity": rarity,
                field_type: file_id,
                "file_id": file_id
            }},
            upsert=True
        )
        success += 1

    print("✅ Sync finished!")
    print(f"📄 Total messages scanned: {total}")
    print(f"🖼️ Images saved: {img_count}")
    print(f"🎞️ Videos saved: {vid_count}")
    print(f"✅ Inserted/Updated: {success}")
    print(f"❌ Failed/Skipped: {fail}")

    client.disconnect()

if __name__ == "__main__":
    main()
