from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from shivu import application, top_global_groups_collection, pm_users

AUTHORIZED_BROADCASTER = 7795212861

async def broadcast(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != AUTHORIZED_BROADCASTER:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    message_to_broadcast = update.message.reply_to_message
    if message_to_broadcast is None:
        await update.message.reply_text("⚠️ Please reply to a message to broadcast.")
        return

    # Fetch all group IDs and user IDs
    all_groups = await top_global_groups_collection.distinct("group_id")
    all_pm_users = await pm_users.distinct("_id")

    total_groups = len(all_groups)
    total_users = len(all_pm_users)

    success_groups = 0
    success_users = 0
    failed = 0

    # Send to groups
    for group_id in all_groups:
        try:
            await context.bot.forward_message(
                chat_id=group_id,
                from_chat_id=message_to_broadcast.chat_id,
                message_id=message_to_broadcast.message_id
            )
            success_groups += 1
        except Exception as e:
            print(f"[Group] Failed to send to {group_id}: {e}")
            failed += 1

    # Send to PM users
    for user_id in all_pm_users:
        try:
            await context.bot.forward_message(
                chat_id=user_id,
                from_chat_id=message_to_broadcast.chat_id,
                message_id=message_to_broadcast.message_id
            )
            success_users += 1
        except Exception as e:
            print(f"[PM] Failed to send to {user_id}: {e}")
            failed += 1

    # Report message
    report = (
        "<b>📢 Broadcast Report</b>\n"
        f"👥 Groups targeted: <b>{total_groups}</b>\n"
        f"📨 Groups succeeded: <b>{success_groups}</b>\n"
        f"🙋‍♂️ PM users targeted: <b>{total_users}</b>\n"
        f"✅ PM users succeeded: <b>{success_users}</b>\n"
        f"❌ Failed sends: <b>{failed}</b>\n"
        f"✅ <b>Broadcast complete!</b>"
    )

    # Send report in current chat
    await update.message.reply_html("✅ Broadcast finished. Sending report to your PM...")

    # PM the report to broadcaster
    try:
        await context.bot.send_message(chat_id=AUTHORIZED_BROADCASTER, text=report, parse_mode='HTML')
    except Exception as e:
        print(f"Failed to send report to owner: {e}")

# Register the command
application.add_handler(CommandHandler("broadcast", broadcast, block=False))
