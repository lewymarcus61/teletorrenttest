import libtorrent as lt
import time
import datetime
import requests
import os
import asyncio
from pyrogram import types
from delete_module import delete_files_in_directory

async def torrent2magnet(message: types.Message, link):
    global count_error3
    count_error3 = False
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
        count_error12 = await download_magnet(message, magnet_link)
        count_error1, count_error2 = count_error12

    except Exception as e:
        count_error3 = True
        delete_files_in_directory("download")
        await message.reply(f"An Error occured while extracting torrent file: {e}")

    return count_error1, count_error2, count_error3

async def download_magnet(message: types.Message, magnet_link):
    global count_error1, count_error2
    count_error1 = False
    count_error2 = False
    sent_message = await message.reply("Starting to download...")
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
            if down_rate > 1000:
                down_rate = down_rate / 1000
                down_rate_str = f"{down_rate:.1f} Mb/s"
            else:
                down_rate_str = f"{down_rate:.1f} kb/s"
            up_rate = s.upload_rate / 1000
            if up_rate > 1000:
                up_rate = up_rate / 1000
                up_rate_str = f"{up_rate:.1f} Mb/s"
            else:
                up_rate_str = f"{up_rate:.1f} kb/s"
            num_peers = s.num_peers
            num_seeds = s.num_seeds
            state = state_str[s.state]
            file_size = s.total_wanted / (1024 * 1024)  # Convert to MB
            if file_size > 1024:
                file_size = file_size / 1024
                file_size_str = f"{file_size:.2f} GB"
            else:
                file_size_str = f"{file_size:.2f} MB"
            file_name = handle.name()

            await sent_message.edit(
                f"File Name: {file_name}\n\n"
                f"Progress: {progress_com:.2f}%\n\n"
                f"Download Speed: {down_rate_str}\n\n"
                f"Upload Speed: {up_rate_str}\n\n"
                f"Peers: {num_peers}\n\n"
                f"Seeds: {num_seeds}\n\n"
                f"File Size: {file_size_str}\n\n"
                f"State: {state}"
            )

            time.sleep(5)

        end = time.time()
        # global file_path
        # file_path = handle.name()
        file_name = handle.name()
        elapsed_time_min = int((end - begin) // 60)
        elapsed_time_sec = int((end - begin) % 60)
        date_time = datetime.datetime.now()
        print('Elapsed Time:', int((end - begin) // 60), 'min:', int((end - begin) % 60), 'sec:')
        print(datetime.datetime.now())
        await sent_message.edit(
            f"{file_name}\n\n"
            "State: Completed!\n\n"
            f"Time Taken: {elapsed_time_min} min, {elapsed_time_sec} sec\n\n"
            f"Up Time: {date_time}"
        )
        await asyncio.sleep(1)
        await sent_message.delete()

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

    return count_error1, count_error2

