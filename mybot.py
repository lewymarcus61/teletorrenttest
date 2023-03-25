import os
import logging
import asyncio
import time
from archive_handler_module import archive_handle
from torrent_module import torrent2magnet, download_magnet
from findvideo_module import check_file
from drive_splitter_module import make_split
from send_video_module import send_video
from delete_module import delete_files_in_directory
from pyrogram import Client, filters
from config import (
    api_id,
    api_hash,
    bot_token
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create an instance
app = Client("my_bot", api_id, api_hash, bot_token=bot_token)

# Create download/temp directories if they don't exist
download_dir = os.path.join(os.getcwd(), "download")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

temp_dir = os.path.join(os.getcwd(), "temp")
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# define a handler function for the start command
@ app.on_message(filters.command("start"))
async def start_handler(client, message):
    # send a message back to the user
    sent_message = await message.reply("Hello!")
    # wait for 3 seconds
    await asyncio.sleep(1)
    # edit the message to "What may I help?"
    await sent_message.edit("I can download torrent file")
    await asyncio.sleep(1)
    await sent_message.edit("Send /leech to download torrent file.")

# set onetime_lock
onetime_lock = False

# Define a handler function for the /torrent command
@app.on_message(filters.command("leech") & filters.private)
async def handle_link_command(client, message):
    global onetime_lock, sent_message1
    onetime_lock = True
    sent_message1 = await message.reply("Send me a Torrent/Magnet link")

@app.on_message(filters.private & ~filters.command("leech"))
async def leecher(client, message):
    global onetime_lock
    if onetime_lock:
        if message.text.startswith("magnet:?"):
            await sent_message1.delete()
            sent_message = await message.reply("Magnet link detected")
            onetime_lock = False
            await asyncio.sleep(1)
            await message.delete()
            await sent_message.delete()
            count_errors = await download_magnet(message, message.text)
            count_error1, count_error2 = count_errors
            if not count_error1 and not count_error2:
                file_path = 'download'
                await archive_handle(message, file_path)
                file_paths = check_file(file_path)
                for video_path in file_paths:
                    # global caption
                    # Check if the video file exists
                    if os.path.exists(video_path):
                        video_size = os.path.getsize(video_path)
                        if video_size > 2000 * 1024 * 1024:
                            file_pathss = await make_split(message, video_path)
                            for video_path1 in file_pathss:
                                try:
                                    await send_video(client, message.chat.id, message, video_path1)
                                except Exception as e:
                                    await message.reply_text(f"An error occured when uploading video: {e}")
                        else:
                            try:
                                await send_video(client, message.chat.id, message, video_path)
                            except Exception as e:
                                await message.reply_text(f"An error occured when uploading video: {e}")
                    else:
                        # Send an error message if the video file does not exist
                        await message.reply_text('Video file not found!')
                delete_files_in_directory("download")
                delete_files_in_directory("temp")

        elif message.text.endswith(".torrent"):
            await sent_message1.delete()
            sent_message = await message.reply("Torrent link detected")
            onetime_lock = False
            await asyncio.sleep(1)
            await message.delete()
            await sent_message.delete()
            count_errors = await torrent2magnet(message, message.text)
            count_error1, count_error2, count_error3 = count_errors
            if not count_error1 and not count_error2 and not count_error3:
                file_path = 'download'
                await archive_handle(message, file_path)
                file_paths = check_file(file_path)
                for video_path in file_paths:
                    # global caption
                    # Check if the video file exists
                    if os.path.exists(video_path):
                        video_size = os.path.getsize(video_path)
                        if video_size > 2 * 1024 * 1024 * 1024:
                            file_pathss = await make_split(message, video_path)
                            for video_path1 in file_pathss:
                                try:
                                    await send_video(client, message.chat.id, message, video_path1)
                                except Exception as e:
                                    await message.reply_text(f"An error occured when uploading video: {e}")
                        else:
                            try:
                                await send_video(client, message.chat.id, message, video_path)
                            except Exception as e:
                                await message.reply_text(f"An error occured when uploading video: {e}")
                    else:
                        # Send an error message if the video file does not exist
                        await message.reply_text('Video file not found!')
                delete_files_in_directory("download")
                delete_files_in_directory("temp")
        else:
            await message.reply(
                "INVALID LINK!\n\n"
                "Support only Torrent or Magnet link!!\n\n"
                'Send Torrent/Magnet Link'
            )

    else:
        pass

# Start the bot
app.run()


