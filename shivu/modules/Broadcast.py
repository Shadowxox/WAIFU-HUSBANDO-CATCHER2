from telegram import Update
from telegram.ext import CallbackContext, CommandHandler
from shivu import application, top_global_groups_collection, pm_users

AUTHORIZED_BROADCASTER = 7795212861

async def broadcast(update: Update, context: CallbackContext) -> None:
    if update.effective_user.id != AUTHORIZED_BROADCASTER:
        await update.message.reply_text("🚫 You are not authorized to use this command.")
        return

    reply = update.message.reply_to_message
    message_text = update.message.text_html or ""
    message_caption = update.message.caption_html or ""

    if not reply and not (message_text or message_caption):
        await update.message.reply_text("⚠️ Please reply to a message or type a message to broadcast.")
        return

    all_groups = await top_global_groups_collection.distinct("group_id")
    all_pm_users = await pm_users.distinct("_id")

    total_groups = len(all_groups)
    total_users = len(all_pm_users)

    success_groups = 0
    success_users = 0
    failed_sends = 0
    success_pins = 0
    failed_pins = 0

    # Send to groups
    for group_id in all_groups:
        try:
            if reply:
                sent = await context.bot.forward_message(
                    chat_id=group_id,
                    from_chat_id=reply.chat_id,
                    message_id=reply.message_id
                )
            else:
                sent = await context.bot.send_message(
                    chat_id=group_id,
                    text=message_text or message_caption,
                    parse_mode="HTML"
                )

            success_groups += 1

            # Try to pin
            try:
                await context.bot.pin_chat_message(chat_id=group_id, message_id=sent.message_id, disable_notification=True)
                success_pins += 1
            except Exception as e:
                print(f"[PIN FAILED] {group_id}: {e}")
                failed_pins += 1

        except Exception as e:
            print(f"[SEND FAILED] Group {group_id}: {e}")
            failed_sends += 1

    # Send to PM users
    for user_id in all_pm_users:
        try:
            if reply:
                await context.bot.forward_message(
                    chat_id=user_id,
                    from_chat_id=reply.chat_id,
                    message_id=reply.message_id
                )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=message_text or message_caption,
                    parse_mode="HTML"
                )
            success_users += 1
        except Exception as e:
            print(f"[PM FAILED] {user_id}: {e}")
            failed_sends += 1

    # Final Report
    report = (
        "<b>📢 Broadcast Report</b>\n\n"
        f"👥 Groups targeted: <b>{total_groups}</b>\n"
        f"📨 Groups succeeded: <b>{success_groups}</b>\n"
        f"📌 Pinned successfully: <b>{success_pins}</b>\n"
        f"📌 Pin failed: <b>{failed_pins}</b>\n\n"
        f"🙋‍♂️ PM users targeted: <b>{total_users}</b>\n"
        f"✅ PM users succeeded: <b>{success_users}</b>\n"
        f"❌ Total failed sends: <b>{failed_sends}</b>\n"
        f"✅ <b>Broadcast complete!</b>"
    )

    await update.message.reply_html("✅ Broadcast finished. Sending report to your PM...")

    try:
        await context.bot.send_message(chat_id=AUTHORIZED_BROADCASTER, text=report, parse_mode='HTML')
    except Exception as e:
        print(f"[REPORT FAILED] Failed to send report: {e}")

# Register the command
application.add_handler(CommandHandler("broadcast", broadcast, block=False))
