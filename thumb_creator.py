import cv2
from PIL import Image
import os
import random
import string
import logging

def create_thumbnail(video_path, duration=None):
    # set thumbnail size and quality
    thumb_size = (320, 320)
    thumb_quality = 80

    # read the video file and extract the frame at the specified duration
    cap = cv2.VideoCapture(video_path)
    if duration is not None:
        cap.set(cv2.CAP_PROP_POS_MSEC, duration * 1000)
    ret, frame = cap.read()

    # check if the frame was extracted successfully
    if not ret:
        return None

    # resize the frame to the thumbnail size
    img = Image.fromarray(frame)
    img.thumbnail(thumb_size)

    # generate a random filename for the thumbnail
    video_dir = os.path.dirname(video_path)
    video_name = os.path.basename(video_path)
    thumb_name = ''.join(random.choices(string.ascii_lowercase + string.digits, k=8)) + '.jpg'
    thumb_path = os.path.join(video_dir, thumb_name)

    # save the thumbnail image as JPEG
    img.convert('RGB').save(thumb_path, "JPEG", quality=thumb_quality, optimize=True)

    # check if the file size is less than 200 KB
    if os.path.getsize(thumb_path) > 200000:
        os.remove(thumb_path)
        return None

    return thumb_path

