import asyncio
import os
from thumb_creator import create_thumbnail
from video_info_module import get_video_info
from pyrogram import Client, types

# Keep track of the progress while uploading
async def progress(current, total):
    global caption
    if current % (5 * 1024 * 1024) == 0:
        print(f"{current * 100 / total:.1f}%")
        await sent_message.edit(
            f"File Name: {caption}\n\n"
            f"Uploading Progress: {current * 100 / total:.1f}%\n\n"
            "State: Uploading"
        )
    else:
        pass

async def send_video(client: Client, chat_id: int, message: types.Message, video_path: str):
    global caption, sent_message
    caption = os.path.basename(video_path)
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
        sent_message = await message.reply_text('Starting to Upload...')
        with open(video_path, "rb") as video_file:
            await client.send_video(
                chat_id,
                video_file,
                width=width,
                height=height,
                duration=duration,
                thumb=thumb_path,
                caption=caption,
                supports_streaming=True,
                disable_notification=True,
                progress=progress
            )
        await sent_message.delete()
        if check_thumb and os.path.exists(thumb_path):
            os.remove(thumb_path)
        else:
            pass
    else:
        await message.reply_text('Failed to Extract Video INFO')

