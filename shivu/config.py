class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7481211733"
    sudo_users = "6861852788", "7378476666", "7481211733", "1167693321", "6861906489", "984844065", "1238713819", "8183658782", "8134602296", "1496149228"
    GROUP_ID = -1002337505439

    TOKEN = "6832094998:AAFr9ukEpdTJ--LyasNV95yD_5X-_wQRdU0"
    mongo_url = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net/"
    PARTNER = "7370569442", "6861852788", "7378476666"
    PHOTO_URL = ["https://files.catbox.moe/7vr2im.jpg", "https://files.catbox.moe/7vr2im.jpg"]
    SUPPORT_CHAT = "-1002337505439"
    UPDATE_CHAT = "-1002337505439"
    BOT_USERNAME = "Catch_your_harem_bot"
    CHARA_CHANNEL_ID = "-1002337505439"
    api_id = 22451491
    api_hash = "28e74942125f7e4968398ea651cd417b"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
