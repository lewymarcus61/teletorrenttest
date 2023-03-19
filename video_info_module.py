from hachoir.parser import createParser
from hachoir.metadata import extractMetadata
from hachoir.core.tools import makePrintable
from subprocess import check_output
from json import loads as jsonloads

def get_video_info(video_path):
    try:
        parser = createParser(video_path)
        metadata = extractMetadata(parser)
        width = metadata.get('width') if metadata.has('width') else get_video_width(video_path)
        height = metadata.get('height') if metadata.has('height') else get_video_height(video_path)
        duration = metadata.get('duration').seconds if metadata.has('duration') else get_video_duration(video_path)
        return width, height, duration
    except Exception as e:
        print(f'Error getting video dimensions: {e}')
        return None, None, None
        
def get_video_width(video_path):
    try:
        result = check_output([
            "ffprobe", "-hide_banner", "-loglevel", "error",
            "-select_streams", "v:0", "-show_entries", "stream=width",
            "-of", "json", video_path
        ]).decode('utf-8')
        fields = jsonloads(result)['streams'][0]

        width = int(fields['width'])
        return width
    except Exception as e:
        print(f'Error getting video info: {e}')
        return None

def get_video_height(video_path):
    try:
        result = check_output([
            "ffprobe", "-hide_banner", "-loglevel", "error",
            "-select_streams", "v:0", "-show_entries", "stream=height",
            "-of", "json", video_path
        ]).decode('utf-8')
        fields = jsonloads(result)['streams'][0]

        height = int(fields['height'])
        return height
    except Exception as e:
        print(f'Error getting video info: {e}')
        return None

def get_video_duration(video_path):
    try:
        result = check_output([
            "ffprobe", "-hide_banner", "-loglevel", "error",
            "-select_streams", "v:0", "-show_entries", "stream=duration",
            "-of", "json", video_path
        ]).decode('utf-8')
        fields = jsonloads(result)['streams'][0]

        duration = float(fields['duration'])
        return duration
    except Exception as e:
        print(f'Error getting video info: {e}')
        return None

