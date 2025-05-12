
import random
import string
import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from shivu import application, user_collection, waifu_collection

SHOP_COSTS = {
    "⚪️ Common": 400,
    "🟢 Medium": 6000,
    "🟣 Rare": 800,
    "🟡 Legendary": 8000,
    "💮 Special Edition": 20000,
    "🔮 Limited Edition": 25000,
    "🎐 Celestial": 35000,
    "🔞 Erotic": 80000,
    "💝 Valentine Special": 45000,
    "❄️ Winter Special": 48000,
    "🌤️ Summer Special": 50000,
    "🎃 Halloween Special": 46000,
    "🧬 X Verse": 40000,
    "💫 Angelic": 150000
}

RARITY_KEYS = list(SHOP_COSTS.keys())

SHOP_USER_STATE = {}
SPIN_CODES = {}
AUTHORIZED_USER = 7795212861
GUESS_GROUP_ID = -1002643948280
CURRENT_WAIFU = {"id": None, "name": None, "time": None, "guessed_by": None}

def generate_code():
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=6))

async def shop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton(rarity, callback_data=f"rarity_{rarity}")] for rarity in RARITY_KEYS]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("🎡 Choose a rarity to spin:", reply_markup=reply_markup)

async def shop_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("rarity_"):
        rarity = data.split("rarity_")[1]
        user_id = query.from_user.id
        SHOP_USER_STATE[user_id] = rarity

        try:
            await context.bot.send_message(chat_id=user_id, text="✅ Tap confirm below to get your waifu spin code in PM.")
            keyboard = [[InlineKeyboardButton("✅ Confirm", callback_data="confirm_spin")]]
            await query.edit_message_text(
                text="🔐 Please tap confirm after messaging the bot in DM/PM.

🔁 /start in private if not started.

🛑 *NOTE:* Code will be given in private only.

🔵 पर्सनल में बॉट को मैसेज करो और फिर Confirm दबाओ। Code वहीं मिलेगा।",
                parse_mode="Markdown",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except:
            await query.edit_message_text("❌ Please start the bot in PM first.")

    elif data == "confirm_spin":
        user_id = query.from_user.id
        chat_type = query.message.chat.type
        if chat_type != "private":
            await query.answer("❗ Confirm in PM/DM only.", show_alert=True)
            return

        rarity = SHOP_USER_STATE.get(user_id)
        if not rarity:
            await query.answer("Please select a rarity first.", show_alert=True)
            return

        cost = SHOP_COSTS.get(rarity, 0)
        user = await user_collection.find_one({"id": user_id})
        balance = user.get("coins", 0) if user else 0

        if balance < cost:
            await query.edit_message_text("❌ Not enough coins to spin.")
            return

        await user_collection.update_one({"id": user_id}, {"$inc": {"coins": -cost}}, upsert=True)
        waifus = waifu_collection.find({"caption": {"$regex": f"(?i)Rarity: {rarity}"}})
        waifu_list = [w async for w in waifus]
        if not waifu_list:
            await query.edit_message_text("No waifus found for this rarity.")
            return

        waifu = random.choice(waifu_list)
        waifu_id = waifu["caption"].split("ID:")[-1].strip()
        code = generate_code()
        SPIN_CODES[code] = {"waifu_id": waifu_id, "quantity": 1}

        await context.bot.send_message(chat_id=user_id, text=f"🎁 Your waifu code: `{code}`
Use `/redeem {code}` to claim!", parse_mode="Markdown")
        await query.edit_message_text("✅ Code has been sent to your DM/PM.")

async def redeem(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args
    if not args:
        await update.message.reply_text("Usage: /redeem <code>")
        return
    code = args[0]
    if code in SPIN_CODES:
        data = SPIN_CODES[code]
        waifu_id = data["waifu_id"]
        if data["quantity"] > 0:
            await user_collection.update_one({"id": user_id}, {"$addToSet": {"waifus": waifu_id}}, upsert=True)
            data["quantity"] -= 1
            if data["quantity"] == 0:
                del SPIN_CODES[code]
            await update.message.reply_text("✅ Waifu successfully added to your collection!")
        else:
            await update.message.reply_text("❌ This code has already been used.")
    else:
        await update.message.reply_text("❌ Invalid code.")

async def rgen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != AUTHORIZED_USER:
        await update.message.reply_text("Unauthorized.")
        return
    try:
        waifu_id = context.args[0]
        quantity = int(context.args[1])
    except:
        await update.message.reply_text("Usage: /rgen <waifu_id> <quantity>")
        return
    code = generate_code()
    SPIN_CODES[code] = {"waifu_id": waifu_id, "quantity": quantity}
    await update.message.reply_text(f"✅ Generated code: `{code}`
Redeem with `/redeem {code}`", parse_mode="Markdown")

async def nguess(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GUESS_GROUP_ID:
        return

    waifus = waifu_collection.aggregate([{"$sample": {"size": 1}}])
    waifu = await waifus.__anext__()
    caption = waifu["caption"]
    name_line = caption.split("\n")[0]
    waifu_name = name_line.split(":", 1)[-1].strip()

    CURRENT_WAIFU.update({
        "id": waifu.get("_id"),
        "name": waifu_name.lower(),
        "time": datetime.datetime.utcnow(),
        "guessed_by": None
    })

    await update.message.reply_photo(photo=waifu["photo"], caption="🧠 Guess the waifu name! (reply not required)
⏱️ You have 5 minutes.")

async def message_listener(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.id != GUESS_GROUP_ID:
        return

    msg = update.message.text.lower()
    user_id = update.effective_user.id

    if not CURRENT_WAIFU["name"]:
        return

    elapsed = (datetime.datetime.utcnow() - CURRENT_WAIFU["time"]).total_seconds()
    if elapsed > 300:
        return

    if msg == CURRENT_WAIFU["name"] and CURRENT_WAIFU["guessed_by"] is None:
        CURRENT_WAIFU["guessed_by"] = user_id
        await user_collection.update_one({"id": user_id}, {"$inc": {"coins": 30}}, upsert=True)
        await update.message.reply_text(f"🎉 Correct! You've earned 30 coins.")

# Register handlers
application.add_handler(CommandHandler("shop", shop))
application.add_handler(CallbackQueryHandler(shop_button, pattern="^(rarity_|confirm_spin)"))
application.add_handler(CommandHandler("redeem", redeem))
application.add_handler(CommandHandler("rgen", rgen))
application.add_handler(CommandHandler("nguess", nguess))
application.add_handler(MessageHandler(filters.TEXT & filters.Chat(GUESS_GROUP_ID), message_listener))
