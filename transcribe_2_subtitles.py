import speech_recognition as sr

# from pydub import AudioSegment
import os
import pysrt

# import translators
from pathlib import Path
import glob
import shutil
import time
import subprocess
import json
from datetime import datetime
import pathvalidate
import time

# import json


VIDEO_DIR = "./downloads"
SUBTITLE_DIR = "./downloads/subs"

# try:
#     with open(CONFIG_FILE, "w") as read_file:
#         json.dump(CONFIGS, read_file)
# except Exception as ex:
#     print(ex)

os.makedirs(SUBTITLE_DIR, exist_ok=True)

# video_file = r"D:\Code\Playground\Subs\24 Peppa Pig Chinese -3DiMC6wWnc4-480pp-1688565567.mp4"

""" Get video file's first stream's width and height

    Requires ffmpeg installed
"""


def movie_resolution(input_file):
    cmds = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 -print_format json -i".split(
        " "
    )
    cmds.append(f"{input_file}")
    # print(cmds)
    metadata = subprocess.check_output(cmds)

    metadata = json.loads(metadata)
    stream0 = metadata["streams"][0]
    width, height = stream0["width"], stream0["height"]
    # print(metadata)

    return width, height


import os
import re
from pytube import YouTube
import requests


def clean_filename(name):
    """Cleans the filename by removing any invalid characters."""
    return re.sub(r"[^a-zA-Z0-9_\- .]", "", name)


def download_file(url, filename):
    """Downloads a file from a URL."""
    response = requests.get(url, stream=True)
    with open(filename, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)


def download_youtube_video(url):
    """Downloads a YouTube video in 720p."""
    yt = YouTube(url)
    stream = yt.streams.filter(res="720p", file_extension="mp4").first()
    if stream:
        filename = clean_filename(yt.title) + ".mp4"
        stream.download(filename=filename)
        return True
    else:
        print(f"720p video not available for {url}")
        return False


def process_urls(file_path):
    """Processes the URLs from the file and downloads content accordingly, removing successfully processed URLs."""
    with open(file_path, "r") as file:
        lines = file.readlines()

    # Skip the first line if it's a comment
    if lines[0].startswith("#"):
        urls = lines[1:]
    else:
        urls = lines

    remaining_urls = []

    for line in urls:
        url = line.strip()
        if not url:
            continue

        print(f"Downloading {url}...")

        try:
            if "youtube.com" in url or "youtu.be" in url:
                success = download_youtube_video(url)
            else:
                filename = os.path.basename(url)
                filename = clean_filename(filename)
                download_file(url, filename)
                success = True

            if not success:
                remaining_urls.append(line)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            remaining_urls.append(line)

    # Write remaining URLs back to the file
    with open(file_path, "w") as file:
        if lines[0].startswith("#"):
            file.write(lines[0])  # Write the comment line
        for url in remaining_urls:
            file.write(url + "\n")


""" Get video file's duration

    Requires ffmpeg installed
"""


def movie_duration(input_file):
    cmds = f"ffprobe -v quiet -print_format json -show_format -hide_banner -i".split(
        " "
    )
    cmds.append(f"{input_file}")
    # print(cmds)
    metadata = subprocess.check_output(cmds)

    metadata = json.loads(metadata)
    length = float(metadata["format"]["duration"])
    # print(metadata)

    return length


WAITING_NEW_FILE = 5

# datetime object containing current date and time

print(f"Waiting for new video files in {VIDEO_DIR}...")


# This required ffmpeg present in system path
def convert_media(input, output):
    if input == output:
        print(f"Input and output are the same: {input}")
        return False

    cmd_str = f'ffmpeg -v quiet -y -i "{input}" "{output}"'

    os.system(cmd_str)
    return True


while True:
    media_files = []

    process_urls(f"{VIDEO_DIR}/urls.txt")

    for media_file in (
        glob.glob(f"{VIDEO_DIR}/*.mp4")
        + glob.glob(f"{VIDEO_DIR}/*.mp3")
        + glob.glob(f"{VIDEO_DIR}/*.m4a")
        + glob.glob(f"{VIDEO_DIR}/*.wav")
    ):
        if not pathvalidate.is_valid_filepath(media_file):
            new_media_file = pathvalidate.sanitize_filepath(media_file)
            new_media_file = new_media_file.replace(" ", "_")
            try:
                shutil.move(media_file, new_media_file)
                media_file = new_media_file
            except Exception as ex:
                print(ex)

        media_files.append(media_file)
        break

    if not media_files:
        # print(f'{datetime.now()} > No video files. Waiting for {WAITING_NEW_FILE}s.')
        time.sleep(WAITING_NEW_FILE)

        continue

    media_file = media_files.pop()

    print(f"Start processing {media_file}...")

    outpath = SUBTITLE_DIR
    video_length = movie_duration(media_file)
    path, filename = os.path.split(media_file)
    base_name, extension = os.path.splitext(filename)
    base_path = os.path.join(outpath, base_name)
    new_media_file = os.path.join(outpath, base_name) + extension

    audio_file = base_path + ".wav"
    mp3_file = base_path + ".mp3"
    sub_zho = base_path + ".zh.srt"
    txt_sub = base_path + ".txt"

    no_text = "^[0-9\n\r]"

    convert_media(media_file, audio_file)
    convert_media(media_file, mp3_file)

    shutil.move(media_file, new_media_file)

    print(f"Audio file exported {audio_file}")

    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()

    # Open the audio file
    with sr.AudioFile(audio_file) as source:
        audio_text = r.record(source)
    # Recognize the speech in the audio

    translations = [False]
    languages = ["zh"]
    sub_files = [sub_zho]

    print(f"Starting transcribing {audio_file}...")

    start = time.time()

    result = r.recognize_whisper(
        audio_text, show_dict=True, word_timestamps=True
    )  # translate=True,
    os.remove(audio_file)
    end = time.time()

    print(
        f"Time elapsed {end - start:.2f} - Video length {video_length:.2f} - relative speed {video_length/(end - start):.1f}x"
    )

    subs = pysrt.SubRipFile()
    sub_idx = 1
    item_count = len(result["segments"])
    lines = []

    for i in range(item_count):
        start_time = result["segments"][i]["start"]
        end_time = result["segments"][i]["end"]
        duration = end_time - start_time
        timestamp = f"{start_time:.3f} - {end_time:.3f}"
        text = result["segments"][i]["text"]

        sub = pysrt.SubRipItem(
            index=sub_idx,
            start=pysrt.SubRipTime(seconds=start_time),
            end=pysrt.SubRipTime(seconds=end_time),
            text=text,
        )
        lines.append(text)
        subs.append(sub)
        sub_idx += 1

        # print(f"{sub_idx}/{item_count}")

    if not subs:
        print(f"Subtitle empty {sub_zho}")

    else:
        subs.save(sub_zho)

        with open(txt_sub, "w", encoding="utf-8") as file:
            file.write("\n".join(lines))

        print(f"Subtitle written {sub_zho}")
        print(f"Waiting for new video files in {VIDEO_DIR}...")
