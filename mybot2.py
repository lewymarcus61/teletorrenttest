import os
import logging
import asyncio
import time
from thumb_creator import create_thumbnail
from video_info1 import get_video_info
from pyrogram import Client, filters
from config import (
    api_id,
    api_hash,
    bot_token
)

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

app = Client("my_bot", api_id, api_hash, bot_token=bot_token)


# Keep track of the progress while uploading
async def progress(current, total):
    print(f"{current * 100 / total:.1f}%")

@app.on_message(filters.command('sendvideo'))
async def send_video(client, message):   
    video_path = 'Tsukimichi Ending Theme 1.mp4'
    # Check if the video file exists
    if os.path.exists(video_path):
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
            start = time.time()
            with open(video_path, "rb") as f:
                await client.send_video(
                    message.chat.id,
                    video=f,
                    width=width,
                    height=height,
                    duration=duration,
                    thumb=thumb_path,
                    caption=caption,
                    supports_streaming=True,
                    disable_notification=True,
                    progress=progress
                )
            end = time.time()
            print(f"elapsed time: {(end-start)/60} min : {(end-start) % 60} sec")
            if check_thumb and os.path.exists(thumb_path):
                os.remove(thumb_path)
            else:
                pass
    else:
        # Send an error message if the video file does not exist
        message.reply_text('Video file not found!')

# Start the bot
app.run()

