import speedtest
import subprocess

async def run_speed_test(download=True, upload=True, ping=False):
    st = speedtest.Speedtest()
    st.get_best_server()
    results = ""

    if download:
        download_speed = st.download() / 1_000_000
        results += f"Download speed: {download_speed:.2f} Mbps\n\n"

    if upload:
        upload_speed = st.upload() / 1_000_000
        results += f"Upload speed: {upload_speed:.2f} Mbps\n"

    if ping:
        ping_time = subprocess.Popen(['ping', '-c', '1', 'google.com'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, error = ping_time.communicate()
        ping_time = out.decode().split('\n')[1].split('time=')[1].split()[0]
        results += f"Ping time: {ping_time} ms\n"

    return results.strip()
