class Config(object):
    LOGGER = True

    # Get this value from my.telegram.org/apps
    OWNER_ID = "7481211733"
    sudo_users = "1496149228", "2022832277", "6925950092", "8134602296", "5877629357", "6861906489", "7152534468"
    GROUP_ID = -1002337505439

    TOKEN = "7686081397:AAGe1wG2M_NsLHl_X5BLXzh88nv6Vmc6kZ0"
    mongo_url = "mongodb+srv://naruto:hinatababy@cluster0.rqyiyzx.mongodb.net/"
    PARTNER = "7370569442", "6861852788", "7378476666"
    PHOTO_URL = ["https://files.catbox.moe/7vr2im.jpg", "https://files.catbox.moe/7vr2im.jpg"]
    SUPPORT_CHAT = "-1002337505439"
    UPDATE_CHAT = "-1002337505439"
    BOT_USERNAME = "@Capture_your_character_robot"
    CHARA_CHANNEL_ID = "-1002337505439"
    api_id = 26977255
    api_hash = "f1d4b2272a2fd50ecdae431ca43fc045"


class Production(Config):
    LOGGER = True


class Development(Config):
    LOGGER = True
