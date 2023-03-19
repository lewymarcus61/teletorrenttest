import os
import logging
import asyncio
import time
import re
import datetime
import requests
import libtorrent as lt
from thumb_creator import create_thumbnail
from video_info_module import get_video_info
from splitter_module import split_file
from findvideo_module import check_file
from delete_module import delete_files_in_directory
from pyrogram import Client, filters
from config import (
    api_id,
    api_hash,
    bot_token
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# Create input/output directories if they don't exist
download_dir = os.path.join(os.getcwd(), "download")
if not os.path.exists(download_dir):
    os.makedirs(download_dir)

temp_dir = os.path.join(os.getcwd(), "temp")
if not os.path.exists(temp_dir):
    os.makedirs(temp_dir)

# Create an instance
app = Client("my_bot", api_id, api_hash, bot_token=bot_token)

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
    await sent_message.edit("Send /torrent to download torrent file.")
    
# define a regex pattern to match URLs
url_pattern = re.compile(r"http(s)?://\S+")

# set onetime_lock
onetime_lock = False

# Define a handler function for the /torrent command
@app.on_message(filters.command("torrent") & filters.private)
async def handle_link_command(client, message):
    global onetime_lock
    onetime_lock = True
    await message.reply("Send me a direct download link to torrent file!")

# Keep track of the progress while uploading
async def progress(current, total):
    global caption
    #print(f"{current * 100 / total:.1f}%")
    await sent_message.edit(
        f"File Name: {caption}\n\n"
        f"Uploading Progress: {current * 100 / total:.1f}%\n\n"
        "State: Uploading"
    )

@app.on_message(filters.private & ~filters.command("torrent"))
async def send_video(client, message):
    global onetime_lock
    if onetime_lock:
        try:
            # Check if the message contains a URL
            if url_pattern.search(message.text):
                global count_error1, count_error2, count_error3
                count_error1 = False
                count_error2 = False
                count_error3 = False
                # Save the URL in the text file
                onetime_lock = False
                link = message.text
                global sent_message
                sent_message = await message.reply("Extracting torrent file from link...")
                try:
                    # Send a GET request to the link to download the torrent file
                    response = requests.get(link)
                    # Extract the filename from the link
                    filename = os.path.basename(link)
                    # Save the response content to a file with the same filename as the link
                    with open(filename, "wb") as f:
                        f.write(response.content)
                    # Load the torrent file
                    with open(filename, 'rb') as f:
                        torrent_data = f.read()
                    # Create a torrent info object
                    torrent_info = lt.torrent_info(torrent_data)
                    # Create a magnet link from the torrent info object
                    magnet_link = lt.make_magnet_uri(torrent_info)
                    # Delete torrent file
                    os.remove(filename)
                    await sent_message.edit("Starting to download...")
                    ses = lt.session()
                    ses.listen_on(6881, 6891)
                    params = {'save_path': 'download', 'storage_mode': lt.storage_mode_t(2)}
                    try:
                        handle = lt.add_magnet_uri(ses, magnet_link, params)
                        ses.start_dht()

                        begin = time.time()
                        await sent_message.edit('Downloading metadata...')

                        num_retries = 0
                        while (not handle.has_metadata()):
                            status = handle.status()

                            if status.state == lt.torrent_status.paused:
                                await sent_message.edit("Please check that the magnet link is correct and try again.")
                                break
                            elif num_retries > 100:
                                break
                            else:
                                pass
                            num_retries += 1
                            time.sleep(1)

                        while (handle.status().state != lt.torrent_status.seeding):
                            s = handle.status()
                            state_str = ['queued', 'checking', 'downloading metadata', 'downloading', 'finished',
                                         'seeding', 'allocating']

                            progress_com = s.progress * 100
                            down_rate = s.download_rate / 1000
                            up_rate = s.upload_rate / 1000
                            num_peers = s.num_peers
                            num_seeds = s.num_seeds
                            state = state_str[s.state]
                            file_size = s.total_wanted / (1024 * 1024)  # Convert to MB
                            file_name = handle.name()

                            await sent_message.edit(
                                f"File Name: {file_name}\n\n"
                                f"Progress: {progress_com:.2f}%\n\n"
                                f"Download Rate: {down_rate:.1f} kb/s\n\n"
                                f"Upload Rate: {up_rate:.1f} kb/s\n\n"
                                f"Peers: {num_peers}\n\n"
                                f"Seeds: {num_seeds}\n\n"
                                f"File Size: {file_size:.2f} MB\n\n"
                                f"State: {state}"
                            )

                            time.sleep(3)

                        end = time.time()
                        global file_path
                        file_path = handle.name()
                        file_name = handle.name()
                        elapsed_time_min = int((end - begin) // 60)
                        elapsed_time_sec = int((end - begin) % 60)
                        date_time = datetime.datetime.now()
                        print('Elapsed Time:', int((end - begin) // 60), 'min:', int((end - begin) % 60), 'sec:')
                        print(datetime.datetime.now())
                        await sent_message.edit(
                            f"{file_name}\n\n"
                            "State: Completed!"
                            f"Time Taken: {elapsed_time_min} min, {elapsed_time_sec} sec\n\n"
                            f"Up Time: {date_time}"
                        )
                        await asyncio.sleep(1)

                    except ValueError as e:
                        count_error1 = True
                        delete_files_in_directory("download")
                        await sent_message.edit("The provided link is invalid.")

                    except Exception as e:
                        count_error2 = True
                        delete_files_in_directory("download")
                        await sent_message.edit(f"An error occurred while downloading the torrent: {e}")

                    finally:
                        ses.pause()
                        ses.remove_torrent(handle)


                except Exception as e:
                    count_error3 = True
                    delete_files_in_directory("download")
                    await sent_message.edit(f"An Error occured while extracting torrent file: {e}")

                if not count_error1 and not count_error2 and not count_error3:
                    file_path = handle.name()
                    file_paths = check_file(file_path)
                    for video_path in file_paths:
                        global caption

                        # Check if the video file exists
                        if os.path.exists(video_path):
                            video_size = os.path.getsize(video_path)
                            if video_size > 2 * 1024 * 1024 * 1024:
                                await message.reply_text(
                                    "This file exceeds 2GB\n\n"
                                    f"File size: {video_size}\n\n"
                                    "Trying to split, Please Wait..."
                                )
                                # input_file_path = video_path
                                output_directory_path = "temp/"
                                split_size = 2097152000
                                equal_splits = False
                                split_file(video_path, output_directory_path, split_size, equal_splits)
                                await sent_message.edit("Done splitting, Starting to upload!")
                                for root, dirs, files in os.walk("temp"):
                                    for filename in files:
                                        global caption
                                        # Print the file path
                                        # print(os.path.join(root, filename))
                                        video_path = os.path.join(root, filename)
                                        caption = os.path.basename(video_path)
                                        # Get the video info
                                        dimensions = get_video_info(video_path)
                                        if dimensions:
                                            width, height, duration = dimensions
                                            thumb_path = None
                                            if duration < 60:
                                                check_thumb = False
                                            else:
                                                check_thumb = True
                                                try:
                                                    thumb_path = create_thumbnail(video_path, duration=(duration / 4))
                                                except:
                                                    pass
                                            # Send the video to the user
                                            await client.send_video(
                                                message.chat.id,
                                                video_path,
                                                width=width,
                                                height=height,
                                                duration=duration,
                                                thumb=thumb_path,
                                                caption=caption,
                                                supports_streaming=True,
                                                disable_notification=True,
                                                progress=progress
                                            )
                                            if check_thumb and os.path.exists(thumb_path):
                                                os.remove(thumb_path)
                                            else:
                                                pass

                            else:
                                await sent_message.edit("Starting to upload...")
                                caption = os.path.basename(video_path)
                                # Get the video info
                                dimensions = get_video_info(video_path)
                                if dimensions:
                                    width, height, duration = dimensions
                                    thumb_path = None
                                    if duration < 60:
                                        check_thumb = False
                                    else:
                                        check_thumb = True
                                        try:
                                            thumb_path = create_thumbnail(video_path, duration=(duration / 4))
                                        except:
                                            pass
                                    # Send the video to the user

                                    await client.send_video(
                                        message.chat.id,
                                        video_path,
                                        width=width,
                                        height=height,
                                        duration=duration,
                                        thumb=thumb_path,
                                        caption=caption,
                                        supports_streaming=True,
                                        disable_notification=True,
                                        progress=progress
                                    )
                                    await sent_message.edit("Upload Completed")
                                    await asyncio.sleep(1)
                                    await sent_message.delete()
                                    if check_thumb and os.path.exists(thumb_path):
                                        os.remove(thumb_path)
                                    else:
                                        pass
                                else:
                                    await sent_message.edit("Failed to upload video!")
                        else:
                            # Send an error message if the video file does not exist
                            message.reply_text('Video file not found!')
                    delete_files_in_directory("download")
                    delete_files_in_directory("temp")


            else:
                await message.reply("Invalid link")
        except Exception as e:
            logging.error(e)
            await message.reply("An error occurred")

    else:
        await message.reply("Can't use")

# Start the bot
app.run()

