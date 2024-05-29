import glob
import json
import os
import re
import shlex
import shutil
import subprocess
import time
from datetime import datetime
from pathlib import Path

import pathvalidate
import pinyin
import pysrt
import speech_recognition as sr
import translators
from gooey import Gooey, GooeyParser

# Constants
MEDIA_DIR = "./downloads"
URL_FILE = "./downloads/urls.txt"
SUBTITLE_DIR = "./downloads/subs"
TRANSLATOR_SERVICE = "baidu"  # Define the default translator service here


def process_urls(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if lines[0].startswith("#"):
        urls = lines[1:]
    else:
        urls = lines

    remaining_urls = []

    for line in urls:
        url = line.strip()
        if not url:
            continue

        filename = None
        if "\t" in line:
            parts = line.split("\t")
            url = parts[0].strip()
            filename = parts[1].strip()

        print(f"Downloading {url}...")

        try:
            if "youtube.com" in url or "youtu.be" in url:
                success = download_youtube_video(url)
            else:
                if not filename:
                    filename = os.path.basename(url)
                filename = clean_filename(filename)
                download_file(url, filename)
                success = True

            if not success:
                remaining_urls.append(line)
        except Exception as e:
            print(f"Failed to download {url}: {e}")
            remaining_urls.append(line)

    with open(file_path, "w") as file:
        if lines[0].startswith("#"):
            file.write(lines[0])
        for url in remaining_urls:
            file.write(url + "\n")


from urllib.parse import urlparse

import requests


def download_file(url, filename):
    response = requests.get(url, stream=True)
    parsed_url = urlparse(url)
    original_filename = os.path.basename(parsed_url.path)
    extension = os.path.splitext(original_filename)[1]

    sanitized_filename = pathvalidate.sanitize_filename(filename)
    new_filename = sanitized_filename + extension
    filepath = os.path.join(MEDIA_DIR, new_filename)

    if os.path.exists(filepath):
        print(f"File {new_filename} already exists, skipping download.")
        return False

    with open(filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return True


@Gooey(program_name="Media Transcriber")
def main():
    global MEDIA_DIR
    global SUBTITLE_DIR
    global TRANSLATOR_SERVICE

    parser = GooeyParser(description="Transcriber Media & Translate Subtitles")

    parser.add_argument(
        "media_dir",
        metavar="Media Directory",
        action="store",
        default=MEDIA_DIR,
        help="Directory containing media files",
    )

    parser.add_argument(
        "subtitle_dir",
        metavar="Subtitle Directory",
        action="store",
        default=SUBTITLE_DIR,
        help="Directory to store subtitle files",
    )

    parser.add_argument(
        "translator_service",
        metavar="Translator Service",
        action="store",
        default=TRANSLATOR_SERVICE,
        help="Translation service to use (e.g., baidu, google, etc.)",
    )

    args = parser.parse_args()

    MEDIA_DIR = args.media_dir
    SUBTITLE_DIR = args.subtitle_dir
    TRANSLATOR_SERVICE = args.translator_service

    os.makedirs(SUBTITLE_DIR, exist_ok=True)

    iteration_count = 0
    max_iterations = 10  # or some appropriate number based on your requirements

    while iteration_count < max_iterations:
        process_urls(URL_FILE)
        if not transcribe_media(5) and not check_for_subtitles(SUBTITLE_DIR):
            break
        iteration_count += 1

    print("Processing completed.")


def has_valid_extension(filename):
    valid_extensions = {".mp4", ".mp3", ".m4a"}
    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in valid_extensions


def transcribe_media(WAITING_NEW_FILE=5):
    media_files = glob.glob(f"{MEDIA_DIR}/*.*")
    media_files.sort(key=os.path.getmtime, reverse=True)
    srt_files = []

    for input in media_files:
        if has_valid_extension(input):
            filename, _ = os.path.splitext(input)
            srt_file = filename + ".srt"

            if not os.path.exists(srt_file):
                srt_files.append(srt_file)

    if not srt_files:
        time.sleep(WAITING_NEW_FILE)
        return False

    for srt_file in srt_files:
        input_file = srt_file.replace(".srt", ".mp4")
        if os.path.exists(input_file):
            subtitle_dir = Path(SUBTITLE_DIR)
            subtitle_dir.mkdir(parents=True, exist_ok=True)

            base_name = os.path.basename(srt_file).replace(".srt", "")
            file_zh = f"{SUBTITLE_DIR}/{base_name}.zh.srt"

            if not os.path.exists(file_zh):
                print(f"Transcribing {input_file} to {file_zh}")
                try:
                    r = sr.Recognizer()
                    with sr.AudioFile(input_file) as source:
                        audio = r.record(source)

                    text = r.recognize_google(audio, language="zh-CN")
                    with open(file_zh, "w", encoding="utf-8") as file:
                        file.write(text)

                except Exception as e:
                    print(f"Failed to transcribe {input_file}: {e}")

    return True


def check_for_subtitles(subtitle_dir):
    patterns = f"{subtitle_dir}/*.zh.srt"
    return bool(glob.glob(patterns))


def clean_filename(name):
    return pathvalidate.sanitize_filename(name)


def download_youtube_video(url):
    yt = YouTube(url)
    stream = yt.streams.filter(res="720p", file_extension="mp4").first()
    if stream:
        filename = clean_filename(yt.title) + ".mp4"
        stream.download(filename=filename)
        return True
    else:
        print(f"720p video not available for {url}")
        return False


if __name__ == "__main__":
    # main()
    while True:
        print("Waiting for new media files...")
        process_urls(URL_FILE)
        transcribe_media(5)
        check_for_subtitles(SUBTITLE_DIR)
