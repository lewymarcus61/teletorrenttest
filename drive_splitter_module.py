import os
import time
from splitter_module import split_file
from findvideo_module import check_file
from pyrogram import Client, types

async def make_split(message: types.Message, video_path: str):
    video_size = os.path.getsize(video_path)
    filee_name = os.path.basename(video_path)
    video_size = video_size / (1024 * 1024 * 1024)
    sent_message = await message.reply_text(
        "This file exceeds 2GB!\n\n"
        f"File Name: {filee_name}\n\n"
        f"File size: {video_size:.2f} GB\n\n"
        "Trying to split, Please Wait..."
    )
    output_directory_path = "temp/"
    split_size = 1800 * 1024 * 1024
    equal_splits = False
    split_file(video_path, output_directory_path, split_size, equal_splits)
    await sent_message.delete()
    file_path = "temp"
    file_pathss = check_file(file_path)

    return file_pathss

