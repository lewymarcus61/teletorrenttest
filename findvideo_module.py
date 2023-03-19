import os
import mimetypes
import magic

def is_video_file(file_path):
    """Check if the given file is a video file."""
    mime_type, _ = mimetypes.guess_type(file_path)
    if mime_type is not None and 'video' in mime_type:
        return True
    return False
    
def is_video_file1(file_path):
    mime = magic.Magic(mime=True)
    return mime.from_file(file_path).startswith('video')

def check_file(file_path):
    file_paths =[]
    """Check if the given file is a video file or a directory with video files."""
    if os.path.isfile(file_path):
        if is_video_file(file_path):
            file_paths.append(file_path)
            print(f"{file_path} is a video file.")
        else:
            print(f"{file_path} is not a video file.")
    elif os.path.isdir(file_path):
        for root, dirs, files in os.walk(file_path):
            for file in files:
                file_path = os.path.join(root, file)
                if is_video_file1(file_path):
                    file_paths.append(file_path)
                    print(f'Found video file: {file_path}')
    else:
        print(f"{file_path} is not a file or directory.")
    return file_paths
        
