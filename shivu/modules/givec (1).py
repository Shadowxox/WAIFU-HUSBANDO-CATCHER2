from telegram import Update
from telegram.ext import CommandHandler, CallbackContext
from telegram.constants import ParseMode
from shivu import application, sudo_users, collection, user_collection

# /givec waifu_id quantity
async def givec_command(update: Update, context: CallbackContext):
    sender_id = str(update.effective_user.id)

    # Check if sender is a sudo user
    if sender_id not in sudo_users:
        await update.message.reply_text("🚫 This command is VIP-only.")
        return

    # Parse arguments
    try:
        waifu_id = context.args[0]
        quantity = int(context.args[1])
    except (IndexError, ValueError):
        await update.message.reply_text("❌ Usage: /givec <waifu_id> <quantity>")
        return

    # Determine recipient (replied user or sender)
    if update.message.reply_to_message:
        recipient = update.message.reply_to_message.from_user
    else:
        recipient = update.effective_user

    recipient_id = recipient.id
    recipient_name = f"[{recipient.first_name}](tg://user?id={recipient_id})"

    # Fetch waifu
    waifu = await collection.find_one({'id': waifu_id})
    if not waifu:
        await update.message.reply_text("❌ Waifu not found with that ID.")
        return

    # Update user's waifu collection
    for _ in range(quantity):
        await user_collection.update_one(
            {'id': recipient_id},
            {'$push': {'characters': waifu}},
            upsert=True
        )

    # Build response
    response_text = (
        f"🎁 {recipient_name} received **{quantity}x** waifu!\n"
        f"📛 Name: {waifu['name']}\n"
        f"⭐ Rarity: {waifu['rarity']}\n"
        f"🎬 Anime: {waifu['anime']}"
    )

    # Send image and message
    await update.message.reply_photo(
        photo=waifu['img_url'],
        caption=response_text,
        parse_mode=ParseMode.MARKDOWN
    )

# Register command
application.add_handler(CommandHandler("givec", givec_command))
