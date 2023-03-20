import os

VIDEO_SUFFIXES = ("M4V", "MP4", "MOV", "FLV", "WMV", "3GP", "MPG", "WEBM", "MKV", "AVI")
    
def is_video_file(file_path):
    if file_path.upper().endswith(VIDEO_SUFFIXES):
        return file_path
    else:
        pass

def check_file(file_path):
    file_paths =[]
    """Check if the given file is a video file or a directory with video files."""
    if os.path.isdir(file_path):
        for root, dirs, files in os.walk(file_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_video_file(file_path):
                    file_paths.append(file_path)
                    print(f'Found video file: {file_path}')
                    
    elif file_path.upper().endswith(VIDEO_SUFFIXES):
        file_paths.append(file_path)
        print(f"{file_path} is a video file.")
                                
    else:
        print(f"{file_path} is not a file or directory.")
    return file_paths
