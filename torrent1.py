import libtorrent as lt
import time
import datetime
import requests
import os

# Input the torrent link
link = input("Enter a direct download link to torrent file: ")

# Send a GET request to the link to download the torrent file
response = requests.get(link)

# Extract the filename from the link
filename = os.path.basename(link)

# Save the response content to a file with the same filename as the link
with open(filename, "wb") as f:
    f.write(response.content)

print(f"Torrent file '{filename}' downloaded successfully.")

# Load the torrent file
with open(filename, 'rb') as f:
    torrent_data = f.read()

# Create a torrent info object
torrent_info = lt.torrent_info(torrent_data)

# Create a magnet link from the torrent info object
magnet_link = lt.make_magnet_uri(torrent_info)

# Delete torrent file
os.remove(filename)

# Print the magnet link
print(magnet_link)


try:
    ses = lt.session()
    ses.listen_on(6881, 6891)

    params = {
        'save_path': 'download',
        'storage_mode': lt.storage_mode_t(2),
    }

    print(link)

    handle = lt.add_magnet_uri(ses, magnet_link, params)
    ses.start_dht()

    begin = time.time()
    print(datetime.datetime.now())

    print('Downloading Metadata......')
    while(not handle.has_metadata()):
        time.sleep(1)

    print('Got Metadata, Starting Torrent Download')
    print('Starting', handle.name())

    while(handle.status().state != lt.torrent_status.seeding):
        s = handle.status()
        state_str = ['queued', 'checking', 'downloading metadata',\
                     'downloading', 'finished', 'seeding', 'allocating']

        print('%.2f %% complete (down: %.1f kb/s up: %.1f kb/s peers: %d) %s ' % \
              (s.progress * 100 , s.download_rate / 1000 , s.upload_rate / 1000, \
               s.num_peers, state_str[s.state]))

        time.sleep(3)

    end = time.time()
    print(handle.name(), 'COMPLETED')
    print('Elapsed Time:', int((end - begin) // 60), 'min:', int((end - begin) % 60), 'sec:')
    print(datetime.datetime.now())
except Exception as e:
    print('An error occurred:', e)
finally:
    ses.pause()
    ses.remove_torrent(handle)

