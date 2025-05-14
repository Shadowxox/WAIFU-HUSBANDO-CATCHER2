class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7795212861"
    sudo_users = "7795212861", "5758240622", "7361967332"
    GROUP_ID = -1002643948280

    TOKEN = "7369319572:AAEP7YLvQP3FQDwY2jMNpos-Zv9B4bnkctE"
    mongo_url = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net/"
    PARTNER = "7361967332", "7795212861", "5758240622"
    PHOTO_URL = ["https://files.catbox.moe/7vr2im.jpg", "https://files.catbox.moe/7vr2im.jpg"]
    SUPPORT_CHAT = "https://t.me/hwkwjieie"
    UPDATE_CHAT = "https://t.me/DBZ_COMMUNITY_2"
    BOT_USERNAME = "@Dbz_waifubot"
    CHARA_CHANNEL_ID = "-1002621413939"
    api_id = 23287799
    api_hash = "9f4f17dae2181ee22c275b9b40a3c907"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
