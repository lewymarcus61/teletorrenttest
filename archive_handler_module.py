import zipfile
import rarfile
import asyncio
import os
from extractor_module import extract_archive
from pyrogram import Client, types

async def is_archive_file(message: types.Message, file_path):
    if zipfile.is_zipfile(file_path):
        filename = os.path.basename(file_path)
        sent_message = await message.reply(f"Found zip file: {filename}")
        await asyncio.sleep(1)
        await sent_message.delete()
        return file_path
    elif rarfile.is_rarfile(file_path):
        filename = os.path.basename(file_path)
        sent_message = await message.reply(f"Found rar file: {filename}")
        await asyncio.sleep(1)
        await sent_message.delete()
        return file_path
    else:
        pass

async def is_archive_file1(file_path):
    if zipfile.is_zipfile(file_path):
        return True
    elif rarfile.is_rarfile(file_path):
        return True
    else:
        return False

async def archive_handle(message: types.Message, file_path):
    """Check if the given file is a video file or a directory with video files."""
    found_archive = False
    while True:
        if os.path.isdir(file_path):
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    file_path2 = os.path.join(root, file)
                    if await is_archive_file1(file_path2):
                        found_archive = True
                    else:
                        pass
        if found_archive:
            for root, dirs, files in os.walk(file_path):
                for file in files:
                    file_path1 = os.path.join(root, file)
                    if await is_archive_file(message, file_path1):
                        found_archive = False  # Set the flag variable to True if an archive is found
                        try:
                            sent_message = await message.reply("Starting to extract, Please wait...")
                            await extract_archive(file_path1, None)
                            await sent_message.edit("Done extracting")
                            await asyncio.sleep(1)
                            await sent_message.delete()
                            os.remove(file_path1)
                        except Exception as e:
                            await message.reply(f"An error occured while extracting file: {e}")
                            break
        else:
            break





