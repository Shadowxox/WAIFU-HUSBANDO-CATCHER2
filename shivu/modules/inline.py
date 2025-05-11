from telegram import InlineQueryResultVideo
from telegram.ext import InlineQueryHandler
from shivu import user_collection
from shivu import application

import re

async def inline_query(update, context):
    query = update.inline_query.query

    match = re.match(r"collection\.(\d+)", query)
    if not match:
        return

    user_id = int(match.group(1))
    user = await user_collection.find_one({"id": user_id})

    if not user:
        return

    # Filter AMV & Hollywood characters with actual videos
    videos = [
        c for c in user.get("characters", [])
        if c.get("rarity") in [13, 14] and c.get("video_url")
    ]

    results = []
    for idx, character in enumerate(videos[:50]):
        results.append(InlineQueryResultVideo(
            id=str(idx),
            video_url=character['video_url'],
            mime_type="video/mp4",
            title=character['name'],
            caption=f"{character['name']} - {character.get('anime', 'Unknown')}",
            thumb_url=character.get('img_url', '')
        ))

    await update.inline_query.answer(results, cache_time=1)

# Register handler
application.add_handler(InlineQueryHandler(inline_query))
