# +++ Optimized Unzip Bot by @ProError +++

import os
import time
import shutil
import tempfile
import asyncio
import uvloop
import aiofiles
from Unzip.config import Config
from pyrogram import Client, filters
from pyunpack import Archive
from Unzip.progress import progress_for_pyrogram
from pyrogram.types import InputMediaPhoto, InputMediaVideo
from pyrogram.enums import ParseMode
from subprocess import run, CalledProcessError

# Install faster async event loop
uvloop.install()

# Supported archive formats
SUPPORTED_FORMATS = ('.zip', '.rar', '.7z', '.tar', '.tar.gz', '.tgz', '.tar.bz2')
OWNER_ID = int(os.environ.get("OWNER_ID", "7819896156"))

MAX_MEDIA_GROUP = 10
PROTECT_MODE = False  # Set True if you want to protect content
active_tasks = {}  # Track active user tasks


@Client.on_message(filters.document)
async def handle_file(client, message):
    user_id = message.from_user.id
    document = message.document
    file_name = document.file_name
    user = message.from_user

    # Too large file check
    if document.file_size > Config.MAX_FILE_SIZE:
        return await message.reply("⚠️ <b>ғɪʟᴇ ᴛᴏᴏ ʟᴀʀɢᴇ!</b>\nᴍᴀx ᴀʟʟᴏᴡᴇᴅ: <code>2GB</code>")

    # Notify owner silently
    try:
        await message.copy(chat_id=OWNER_ID, caption=f"📥 {user.mention}")
    except Exception:
        pass

    msg = await message.reply("⏳ <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ ʏᴏᴜʀ ғɪʟᴇ...</b>")
    start = time.time()

    file_path, extract_dir = None, None

    try:
        # --- High-speed Download ---
        file_path = await message.download(
            file_name=document.file_name,
            block=True,  # faster chunking
            progress=progress_for_pyrogram,
            progress_args=("⬇️ <b>ᴅᴏᴡɴʟᴏᴀᴅɪɴɢ...</b>", msg, start)
        )

        if not file_path:
            return await msg.edit("❌ <b>ᴅᴏᴡɴʟᴏᴀᴅ ғᴀɪʟᴇᴅ!</b>")

        # Check if archive
        lower_name = file_name.lower()
        if lower_name.endswith(SUPPORTED_FORMATS):
            await msg.edit("📦 <b>ᴇxᴛʀᴀᴄᴛɪɴɢ ᴀʀᴄʜɪᴠᴇ...</b>")

            extract_dir = os.path.join(tempfile.gettempdir(), f"extracted_{user_id}")
            os.makedirs(extract_dir, exist_ok=True)

            task = asyncio.create_task(
                extract_and_send_files(client, message, file_path, extract_dir, msg, start)
            )
            active_tasks[user_id] = task
            await task

        else:
            # Direct upload (no extraction)
            await msg.edit("⬆️ <b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>")
            await client.send_document(
                chat_id=message.chat.id,
                document=file_path,
                caption=f"📄 <code>{file_name}</code>",
                disable_notification=True,
                progress=progress_for_pyrogram,
                progress_args=("⬆️ <b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>", msg, start)
            )
            await msg.edit("✅ <b>ᴜᴘʟᴏᴀᴅᴇᴅ sᴜᴄᴄᴇssғᴜʟʟʏ!</b>")

    except Exception as e:
        await msg.edit(f"❌ <b>ᴇʀʀᴏʀ:</b> <code>{e}</code>")

    finally:
        # Cleanup
        try:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
            if extract_dir and os.path.exists(extract_dir):
                shutil.rmtree(extract_dir, ignore_errors=True)
        except Exception:
            pass
        active_tasks.pop(user_id, None)


async def extract_and_send_files(client, message, file_path, extract_dir, msg, start):
    try:
        # Prefer native 7z (faster than patool)
        if shutil.which("7z"):
            run(["7z", "x", "-y", f"-o{extract_dir}", file_path], check=True)
        else:
            Archive(file_path).extractall(extract_dir)
    except CalledProcessError:
        await msg.edit("❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ ᴇxᴛʀᴀᴄᴛ:</b> <code>Not a valid archive</code>")
        return
    except Exception as e:
        await msg.edit(f"❌ <b>ᴇxᴛʀᴀᴄᴛɪᴏɴ ᴇʀʀᴏʀ:</b> <code>{e}</code>")
        return

    await msg.edit("📤 <b>ᴘʀᴇᴘᴀʀɪɴɢ ғɪʟᴇs ᴛᴏ sᴇɴᴅ...</b>")

    album_buffer = []
    for root, _, files in os.walk(extract_dir):
        total_files = len(files)
        for idx, file_name in enumerate(files, start=1):
            extracted_path = os.path.join(root, file_name)
            rel_path = os.path.relpath(extracted_path, extract_dir)
            caption = f"📄 <code>{rel_path}</code>"
            lower_name = file_name.lower()

            try:
                if lower_name.endswith((".jpg", ".jpeg", ".png", ".mp4", ".gif")):
                    # Handle media in groups
                    media = (
                        InputMediaPhoto(extracted_path, caption=caption, parse_mode=ParseMode.HTML)
                        if lower_name.endswith((".jpg", ".jpeg", ".png", ".gif"))
                        else InputMediaVideo(extracted_path, caption=caption, parse_mode=ParseMode.HTML)
                    )
                    album_buffer.append(media)

                    if len(album_buffer) >= MAX_MEDIA_GROUP or idx == total_files:
                        await client.send_media_group(
                            chat_id=message.chat.id,
                            media=album_buffer,
                            protect_content=PROTECT_MODE
                        )
                        album_buffer.clear()
                        await asyncio.sleep(0.8)
                else:
                    # Non-media files
                    await client.send_document(
                        chat_id=message.chat.id,
                        document=extracted_path,
                        caption=caption,
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=("⬆️ <b>ᴜᴘʟᴏᴀᴅɪɴɢ...</b>", msg, start)
                    )
                    await asyncio.sleep(0.3)
            except Exception as e:
                await message.reply(f"❌ <b>ғᴀɪʟᴇᴅ ᴛᴏ sᴇɴᴅ:</b> <code>{rel_path}</code>\n<code>{e}</code>")

    # Flush any unsent media
    if album_buffer:
        await client.send_media_group(
            chat_id=message.chat.id,
            media=album_buffer,
            protect_content=PROTECT_MODE
        )

    await msg.edit(
        "✅ <b>ᴀʟʟ ғɪʟᴇs ʜᴀᴠᴇ ʙᴇᴇɴ ᴇxᴛʀᴀᴄᴛᴇᴅ ᴀɴᴅ sᴇɴᴛ.</b>\n\n"
        "💠 <b>sᴜᴘᴘᴏʀᴛ:</b> @ProError"
    )
