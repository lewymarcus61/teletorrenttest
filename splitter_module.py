import os
import subprocess
import logging
from subprocess import check_output
from json import loads as jsnloads

VIDEO_SUFFIXES = ("M4V", "MP4", "MOV", "FLV", "WMV", "3GP", "MPG", "WEBM", "MKV", "AVI")

LOGGER = logging.getLogger(__name__)

def get_media_info(path):
    try:
        result = check_output(["ffprobe", "-hide_banner", "-loglevel", "error", "-print_format",
                                          "json", "-show_format", path]).decode('utf-8')
        fields = jsnloads(result)['format']
    except Exception as e:
        LOGGER.error(f"get_media_info: {e}")
        return 0
    try:
        duration = round(float(fields['duration']))
    except:
        duration = 0

    return duration

def split_file(video_path, output_directory_path, split_size, equal_splits):
    input_file_size = os.path.getsize(video_path)
    
    if equal_splits:
        number_of_splits = input_file_size // split_size + (input_file_size % split_size != 0)
        split_size = input_file_size // number_of_splits
    else:
        number_of_splits = input_file_size // split_size + (input_file_size % split_size != 0)
        
    if video_path.upper().endswith(VIDEO_SUFFIXES):
        base_name, extension = os.path.splitext(os.path.basename(video_path))
        split_size = split_size - 2500000
        start_time = 0
        
        for i in range(1, number_of_splits + 1):
            split_file_name = f"{base_name}.part{i:03d}{extension}"
            split_file_path = os.path.join(output_directory_path, split_file_name)
            
            subprocess.run(["ffmpeg","-y", "-hide_banner", "-loglevel", "error", "-i",
                            video_path, "-ss", str(start_time), "-fs", str(split_size),
                            "-async", "1", "-strict", "-2", "-c", "copy", split_file_path])
            
            split_file_size = os.path.getsize(split_file_path)
            
            if split_file_size > 2000000000:
                dif = split_file_size - 2000000000
                split_size = split_size - dif + 104857600
                os.remove(split_file_path)
                split_file(video_path, output_directory_path, split_size, equal_splits=True)
            
            last_packet_duration = get_media_info(split_file_path)
            if last_packet_duration <= 4 or split_file_size < 1000000:
                os.remove(split_file_path)
                break
            
            start_time += last_packet_duration - 3
            
    else:
        split_file_path = f"{video_path}."
        subprocess.run(["split", "--numeric-suffixes=1", "--suffix-length=3", f"--bytes={split_size}", video_path, split_file_path])


