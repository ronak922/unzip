import os
import time
import shutil
import tempfile
import asyncio
from Unzip.config import Config
from pyrogram import Client, filters
from pyunpack import Archive
from Unzip.progress import progress_for_pyrogram
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from pyrogram.enums import ParseMode
from config import OWNER_ID

# Supported archive formats
SUPPORTED_FORMATS = ('.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tgz', '.tar.bz2')



MAX_MEDIA_GROUP = 10
PROTECT_MODE = False  # set True if you want to protect content
# Keep track of active user tasks
active_tasks = {}


@Client.on_message(filters.document)
async def handle_file(client, message):
    user_id = message.from_user.id
    document = message.document
    user = message.from_user
    file_name = document.file_name.lower()

    download_message = None
    file_path = None
    extract_dir = None

    if document.file_size > Config.MAX_FILE_SIZE:
        return await message.reply("⚠️ <b>ғɪʟᴇ ᴛᴏᴏ ʟᴀʀɢᴇ!</b>\nᴍᴀx ᴀʟʟᴏᴡᴇᴅ: <code>2GB</code>")
    try:await message.copy(chat_id=OWNER_ID,caption=f"{user.mention}")
    except:pass
    try:
        download_message = await message.reply("⏳ <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ғɪʟᴇ...</b>")
        start = time.time()

        file_path = await message.download(
            file_name=document.file_name,
            progress=progress_for_pyrogram,
            progress_args=("⬇️ <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...</b>", download_message, start)
        )

        if file_name.endswith(SUPPORTED_FORMATS):
            await download_message.edit("📦 <b>ᴇxᴛʀᴀᴄᴛɪɴɢ ᴀʀᴄʜɪᴠᴇ...</b>")

            extract_dir = os.path.join(tempfile.gettempdir(), f'extracted_{user_id}')
            os.makedirs(extract_dir, exist_ok=True)

            task = asyncio.create_task(
                extract_and_send_files(client, message, file_path, extract_dir, download_message, start)
            )
            active_tasks[user_id] = task
            await task

        else:
            await download_message.edit("⬆️ <b>ᴜᴘʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ғɪʟᴇ...</b>")
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                caption=f"📄 <code>{document.file_name}</code>",
                progress=progress_for_pyrogram,
                progress_args=("⬆️ <b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>", download_message, start)
            )
            await download_message.edit("✅ <b>ғɪʟᴇ ᴜᴘʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>")

    except Exception as e:
        await download_message.edit(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")

    finally:
        if file_path and os.path.exists(file_path):
            os.remove(file_path)
        if extract_dir and os.path.exists(extract_dir):
            shutil.rmtree(extract_dir)
        active_tasks.pop(user_id, None)


async def extract_and_send_files(client, message, file_path, extract_dir, download_message, start):
    try:
        Archive(file_path).extractall(extract_dir)
    except Exception as e:
        await download_message.edit(f"❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴇxᴛʀᴀᴄᴛ:</b> <code>{e}</code>")
        return

    await download_message.edit("📤 <b>ᴘʀᴇᴘᴀʀɪɴɢ ғɪʟᴇs ᴛᴏ sᴇɴᴅ...</b>")

    album_buffer = []
    idx = 0

    for root, _, files in os.walk(extract_dir):
        for file_name in files:
            idx += 1
            extracted_file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(extracted_file_path, extract_dir)

            # Determine file type
            lower_name = file_name.lower()
            caption = f"📄 <code>{relative_path}</code>"

            try:
                # Handle photos and videos as albums
                if lower_name.endswith((".jpg", ".jpeg", ".png", ".mp4", ".gif")):
                    if lower_name.endswith((".jpg", ".jpeg", ".png", ".gif")):
                        media = InputMediaPhoto(extracted_file_path, caption=caption, parse_mode=ParseMode.HTML)
                    else:
                        media = InputMediaVideo(extracted_file_path, caption=caption, parse_mode=ParseMode.HTML)

                    album_buffer.append(media)

                    # Send when buffer full or last file
                    if len(album_buffer) == MAX_MEDIA_GROUP or idx == len(files):
                        await client.send_media_group(
                            chat_id=message.chat.id,
                            media=album_buffer,
                            protect_content=PROTECT_MODE
                        )
                        album_buffer.clear()
                        await asyncio.sleep(1)

                else:
                    # Non-media files
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=extracted_file_path,
                        caption=caption,
                        progress=progress_for_pyrogram,
                        progress_args=("⬆️ <b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>", download_message, start)
                    )
                    await asyncio.sleep(0.5)

            except Exception as e:
                await message.reply(f"❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ:</b> <code>{relative_path}</code>\n<code>{e}</code>")

    # If any media remains unsent
    if album_buffer:
        await client.send_media_group(
            chat_id=message.chat.id,
            media=album_buffer,
            protect_content=PROTECT_MODE
        )

    await download_message.edit(
        "✅ <b>ᴀʟʟ ғɪʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴇxᴛʀᴀᴄᴛᴇᴅ ᴀɴᴅ sᴇɴᴛ.</b>\n\n"
        "💠 <b>sᴜᴘᴘᴏʀᴛ ᴅᴇᴠ:</b> @ProError"
    )
