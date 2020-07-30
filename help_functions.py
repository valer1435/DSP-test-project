import dlib
import io
import os
import traceback
import subprocess
from hashlib import md5
from io import BytesIO
import cv2
import requests
import numpy as np


NEW_SAMPLERATE = "16000"
FFMPEG_PATH = "bin/ffmpeg.exe"
AUDIO_FOLDER = "audio"
PHOTOS_FOLDER = "photos"
detector = dlib.get_frontal_face_detector()
API_TOKEN = ''

def convert_voice_file(old_file_name):
    new_file_name = old_file_name.replace(".ogg", ".wav")
    subprocess.call(
        [FFMPEG_PATH,
         "-i", old_file_name,
         "-ar", NEW_SAMPLERATE,
         new_file_name],
        stderr=subprocess.DEVNULL)
    os.remove(old_file_name)
    return new_file_name


def save_voice_file(file, user_id):
    try:
        user_id_hash = get_md5(str(user_id))
        file_name = f"{AUDIO_FOLDER+os.sep+user_id_hash+os.sep+file['file_id']}.ogg"
        if not os.path.exists(AUDIO_FOLDER):
            os.mkdir(AUDIO_FOLDER)
        if not os.path.exists(AUDIO_FOLDER+os.sep+user_id_hash):
            os.mkdir(AUDIO_FOLDER+os.sep+user_id_hash)
        file.download(file_name)
        convert_voice_file(file_name)
        return True
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return False


def process_photo(file):
    try:
        raw_bytes = requests.get(file.file_path).content
        faces_count, img = detect_faces(raw_bytes)
        if faces_count:
            save_photo(file)
            return faces_count, io.BufferedReader(BytesIO(img))
        return faces_count, io.BufferedReader(BytesIO(raw_bytes))
    except Exception as e:
        traceback.print_tb(e.__traceback__)
        return 0, None


def save_photo(file):
    if not os.path.exists(PHOTOS_FOLDER):
        os.mkdir(PHOTOS_FOLDER)
    file.download(f"{PHOTOS_FOLDER+os.sep+file.file_id}.png")
    return True


def detect_faces(raw_photo):
    image = np.asarray(bytearray(raw_photo), dtype="uint8")
    image_bgr = cv2.imdecode(image, cv2.IMREAD_COLOR)
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)
    faces = detector(image_rgb, 1)
    faces_count = 0
    for i, d in enumerate(faces):
        image_bgr = cv2.rectangle(image_bgr, (d.left(), d.top()), (d.right(), d.bottom()), (0, 255, 0), 3)
        faces_count += 1
    return faces_count, cv2.imencode('.png', image_bgr)[1]


def get_md5(in_string):
    return md5(in_string.encode()).hexdigest()
