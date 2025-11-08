# ©️ LISA-KOREA | @LISA_FAN_LK | ProError | LISA-KOREA/UnZip-Bot

# [⚠️ Do not change this repo link ⚠️] :- https://github.com/LISA-KOREA/UnZip-Bot



from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardButton, InlineKeyboardMarkup

active_tasks = {}


@Client.on_message(filters.command("start"))
async def start(client, message):
    mention = message.from_user.mention  # Get user mention properly

    reply_markup = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📍 ᴜᴘᴅᴀᴛᴇs", url="https://t.me/BhookiBhabhi"),
        ]
    ])

    start_message = (
        f"<b>⚡ Hᴇʏ, {mention} ~!</b>\n\n"
        "<blockquote>"
        "I ᴀᴍ ᴀɴ ᴀᴅᴠᴀɴᴄᴇ ᴢɪᴘ ᴏᴘᴇɴᴇʀ ʙᴏᴛ. Jᴜsᴛ sᴇɴᴅ ᴍᴇ ᴀ ᴢɪᴘ ᴀɴᴅ ɪ ᴡɪʟʟ ᴇxᴛʀᴀᴄᴛ ɪᴛ ғᴏʀ ʏᴏᴜ.\n"
        "» ᴍᴀᴅᴇ ʙʏ <a href='https://t.me/ProError'>@ProError</a>"
        "</blockquote>"
    )

    await message.reply(start_message, reply_markup=reply_markup)


# Callback query handler
@Client.on_callback_query(filters.regex("cancel"))
async def cancel(client, callback_query):
    await callback_query.message.delete()


@Client.on_message(filters.command("help"))
async def help_command(client, message):
    help_message = (
        "Here are the commands you can use:\n\n"
        "/start - Start the bot and get the welcome message\n"
        "/help - Get help on how to use the bot\n\n"
        "To unzip a file, simply send me a ZIP file and I will extract its contents and send them back to you.\n\n"
        "©️ Channel : @ProError"
    )
    await message.reply(help_message)



@Client.on_callback_query(filters.regex("cancel_unzip"))
async def cancel_callback(client, callback_query):
    user_id = callback_query.from_user.id

    if user_id in active_tasks:
        task = active_tasks[user_id]
        task.cancel()
        await callback_query.answer("⛔ Unzipping has been cancelled.", show_alert=True)
    else:
        await callback_query.answer("⚠️ No ongoing unzip operation.", show_alert=True)

