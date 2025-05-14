from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from shivu import user_collection
from shivu import shivuu

pending_trades = {}


@shivuu.on_message(filters.command("trade"))
async def trade(client, message):
    sender_id = message.from_user.id

    if not message.reply_to_message:
        await message.reply_text("You need to reply to a user's message to trade a character!")
        return

    receiver_id = message.reply_to_message.from_user.id

    if sender_id == receiver_id:
        await message.reply_text("You can't trade a character with yourself!")
        return

    if len(message.command) != 3:
        await message.reply_text("You need to provide two character IDs!")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]

    sender = await user_collection.find_one({'id': sender_id})
    receiver = await user_collection.find_one({'id': receiver_id})

    sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
    receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)

    if not sender_character:
        await message.reply_text("You don't have the character you're trying to trade!")
        return

    if not receiver_character:
        await message.reply_text("The other user doesn't have the character they're trying to trade!")
        return






    if len(message.command) != 3:
        await message.reply_text("/trade [Your Character ID] [Other User Character ID]!")
        return

    sender_character_id, receiver_character_id = message.command[1], message.command[2]


    pending_trades[(sender_id, receiver_id)] = (sender_character_id, receiver_character_id)


    keyboard = InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("Confirm Trade", callback_data="confirm_trade")],
            [InlineKeyboardButton("Cancel Trade", callback_data="cancel_trade")]
        ]
    )

    await message.reply_text(f"{message.reply_to_message.from_user.mention}, do you accept this trade?", reply_markup=keyboard)


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data in ["confirm_trade", "cancel_trade"]))
async def on_callback_query(client, callback_query):
    receiver_id = callback_query.from_user.id


    for (sender_id, _receiver_id), (sender_character_id, receiver_character_id) in pending_trades.items():
        if _receiver_id == receiver_id:
            break
    else:
        await callback_query.answer("This is not for you!", show_alert=True)
        return

    if callback_query.data == "confirm_trade":

        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': receiver_id})

        sender_character = next((character for character in sender['characters'] if character['id'] == sender_character_id), None)
        receiver_character = next((character for character in receiver['characters'] if character['id'] == receiver_character_id), None)



        sender['characters'].remove(sender_character)
        receiver['characters'].remove(receiver_character)


        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})


        sender['characters'].append(receiver_character)
        receiver['characters'].append(sender_character)


        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})
        await user_collection.update_one({'id': receiver_id}, {'$set': {'characters': receiver['characters']}})


        del pending_trades[(sender_id, receiver_id)]

        await callback_query.message.edit_text(f"You have successfully traded your character with {callback_query.message.reply_to_message.from_user.mention}!")

    elif callback_query.data == "cancel_trade":

        del pending_trades[(sender_id, receiver_id)]

        await callback_query.message.edit_text("❌️ Sad Cancelled....")




from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
from shivu import user_collection
from shivu import shivuu

# Global variables to track pending gifts, locks, and cooldowns
pending_gifts = {}
locked_users = set()         # Track users currently engaged in any process
locked_characters = set()    # Track characters currently involved in any process
cooldowns = {}               # Track users and their last confirmed gift time


@shivuu.on_message(filters.command("gift"))
async def gift(client, message):
    sender_id = message.from_user.id

    # Check if the user has recently confirmed a gift (1 min cooldown)
    if sender_id in cooldowns:
        time_since_last_gift = time.time() - cooldowns[sender_id]
        if time_since_last_gift < 20:  # Cooldown of 60 seconds
            await message.reply_text(f"⏳ Please wait **{int(60 - time_since_last_gift)} seconds** before gifting again!")
            return

    # Check if the user is locked (in an ongoing process)
    if sender_id in locked_users:
        await message.reply_text("⚠️ **You already have a pending process!** Complete it before starting another or use /dreset.")
        return    

    if not message.reply_to_message:
        await message.reply_text("❗ **Reply to a user's message** to gift a character!")
        return

    receiver_id = message.reply_to_message.from_user.id
    receiver_username = message.reply_to_message.from_user.username
    receiver_first_name = message.reply_to_message.from_user.first_name

    # Prevent gifting to self
    if sender_id == receiver_id:
        await message.reply_text("🙅‍♂️ **You can't gift a character to yourself!**")
        return

    # Ensure the command includes a character ID
    if len(message.command) != 2:
        await message.reply_text("⚙️ **You need to provide a valid character ID!**")
        return

    character_id = message.command[1]

    sender = await user_collection.find_one({'id': sender_id})

    # Check if the sender has the character
    character = next((character for character in sender['characters'] if character['id'] == character_id), None)

    if not character:
        await message.reply_text("❌ **You don't own this character** you are trying to gift!")
        return

    # Check if the character is locked (already in a pending transaction)
    if character_id in locked_characters:
        await message.reply_text("🔒 **This character is already involved in another transaction!**")
        return

    # Lock the user and the character
    locked_users.add(sender_id)
    locked_characters.add(character_id)

    # Create a unique identifier for the gift process (using timestamp)
    process_id = str(time.time())

    # Store pending gift data
    sent_message = await message.reply_text(
        f"🎁 {message.from_user.mention}, do you confirm gifting this character?",
        reply_markup=InlineKeyboardMarkup(
            [
                [InlineKeyboardButton("✅ Confirm Gift", callback_data=f"confirm_gift:{process_id}")],
                [InlineKeyboardButton("❌ Cancel Gift", callback_data=f"cancel_gift:{process_id}")]
            ]
        ))

    pending_gifts[(sender_id, receiver_id)] = {
        'character': character,
        'receiver_username': receiver_username,
        'receiver_first_name': receiver_first_name,
        'process_id': process_id  # Track the unique process ID
    }


@shivuu.on_callback_query(filters.create(lambda _, __, query: query.data.startswith(("confirm_gift:", "cancel_gift:"))))
async def on_callback_query(client, callback_query):
    sender_id = callback_query.from_user.id
    data, process_id = callback_query.data.split(":")

    for (s_id, r_id), gift in list(pending_gifts.items()):
        if s_id == sender_id and gift['process_id'] == process_id:
            break
    else:
        await callback_query.answer("❗ This action is no longer valid!", show_alert=True)
        return

    # Process confirmation or cancellation of gift
    if data == "confirm_gift":
        await callback_query.answer("✅ Gift successfully given!", show_alert=True)

        await callback_query.message.edit_text(
            f"🎉 **You have successfully gifted your character to** [{gift['receiver_first_name']}](tg://user?id={r_id})! 🥳")

        sender = await user_collection.find_one({'id': sender_id})
        receiver = await user_collection.find_one({'id': r_id})

        # Remove the character from the sender's collection
        sender['characters'].remove(gift['character'])
        await user_collection.update_one({'id': sender_id}, {'$set': {'characters': sender['characters']}})

        # Add the character to the receiver's collection
        if receiver:
            await user_collection.update_one({'id': r_id}, {'$push': {'characters': gift['character']}})
        else:
            await user_collection.insert_one({
                'id': r_id,
                'username': gift['receiver_username'],
                'first_name': gift['receiver_first_name'],
                'characters': [gift['character']],
            })

        # Set the cooldown for the sender (1 minute from now)
        cooldowns[sender_id] = time.time()

        # Clean up: remove the lock and pending gift
        del pending_gifts[(sender_id, r_id)]
        locked_users.remove(sender_id)
        locked_characters.remove(gift['character']['id'])

    elif data == "cancel_gift":
        # Remove the pending gift and unlock the user and character
        del pending_gifts[(sender_id, r_id)]
        locked_users.remove(sender_id)
        locked_characters.remove(gift['character']['id'])

        await callback_query.message.edit_text("❌ **Gift process cancelled.**")


@shivuu.on_message(filters.command("dreset"))
async def reset_gift(client, message):
    sender_id = message.from_user.id

    for (s_id, r_id), gift in list(pending_gifts.items()):
        if s_id == sender_id:
            # Remove the pending gift and unlock the user and character
            del pending_gifts[(s_id, r_id)]
            locked_users.discard(sender_id)
            locked_characters.discard(gift['character']['id'])

            # Invalidate any existing callback queries by updating the process ID
            gift['process_id'] = None

            await message.reply_text("🔄 **Your current gift process has been reset.**")

            return

    await message.reply_text("❗ **You don't have any ongoing gift processes to reset.**")
