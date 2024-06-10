import json
import os
import subprocess
from urllib.parse import urlparse

import pathvalidate
import requests
from pytube import YouTube


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
        print(f"720p video not available for {url}", flush=True)
        return False


def wrap_file_name(filename):
    return '"' + filename + '"'


def convert_media(input_file, output_file):
    # Get the path to the ffmpeg executable in the ./bin folder
    ff_path = os.path.join(".", "bin", "ffmpeg")

    # Construct the command to convert the media file
    command = [
        ff_path,
        "-v",
        "quiet",
        "-y",
        "-i",
        input_file,
        output_file,
    ]

    try:
        # Run the command using subprocess
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        return False


def movie_resolution(input_file):

    ff_path = os.path.join(".", "bin", "ffprobe")

    command = [ff_path, "-i", input_file]
    command.extend(
        "-v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 -print_format json".split(
            " "
        )
    )

    metadata = subprocess.check_output(command)
    metadata = json.loads(metadata)
    stream0 = metadata["streams"][0]
    width, height = stream0["width"], stream0["height"]
    return width, height


def movie_duration(input_file):
    ff_path = os.path.join(".", "bin", "ffprobe")

    command = [ff_path, "-i", input_file]

    command.extend("-v quiet -print_format json -show_format -hide_banner".split(" "))

    metadata = subprocess.check_output(command)

    metadata = json.loads(metadata)
    length = float(metadata["format"]["duration"])

    return length


def download_file(url, filename, folder):
    response = requests.get(url, stream=True)
    parsed_url = urlparse(url)
    original_filename = os.path.basename(parsed_url.path)
    extension = os.path.splitext(original_filename)[1]

    sanitized_filename = pathvalidate.sanitize_filename(filename)
    new_filename = sanitized_filename + extension
    filepath = os.path.join(folder, new_filename)

    if os.path.exists(filepath):
        print(f"File {new_filename} already exists, skipping download.", flush=True)
        return False

    with open(filepath, "wb") as file:
        for chunk in response.iter_content(chunk_size=8192):
            file.write(chunk)

    return True


def format_duration(seconds):
    # Calculate hours, minutes, seconds, and milliseconds
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60
    milliseconds = int((remaining_seconds - int(remaining_seconds)) * 1000)

    # Format with leading zeros
    formatted_time = (
        f"{hours:02}:{minutes:02}:{int(remaining_seconds):02}.{milliseconds:03}"
        if hours
        else f"{minutes:02}:{int(remaining_seconds):02}.{milliseconds:03}"
    )

    return formatted_time


availableTranslationLanguages = [
    {"code": "ar", "name": "Arabic", "nativeName": "العربية"},
    {"code": "bg", "name": "Bulgarian", "nativeName": "български език"},
    {"code": "nl", "name": "Dutch", "nativeName": "Nederlands"},
    {"code": "fr", "name": "French", "nativeName": "français"},
    {"code": "de", "name": "German", "nativeName": "Deutsch"},
    {"code": "el", "name": "Greek", "nativeName": "Ελληνικά"},
    {"code": "id", "name": "Indonesian", "nativeName": "Bahasa Indonesia"},
    {"code": "it", "name": "Italian", "nativeName": "Italiano"},
    {"code": "ja", "name": "Japanese", "nativeName": "日本語"},
    {"code": "pl", "name": "Polish", "nativeName": "polski"},
    {"code": "pt", "name": "Portuguese", "nativeName": "Português"},
    {
        "code": "pt-br",
        "name": "Portuguese (Brazil)",
        "nativeName": "Português do Brasil",
    },
    {"code": "ro", "name": "Romanian", "nativeName": "română"},
    {"code": "ru", "name": "Russian", "nativeName": "русский язык"},
    {"code": "es", "name": "Spanish (Spain)", "nativeName": "español (España)"},
    {
        "code": "es-la",
        "name": "Spanish (Latin America)",
        "nativeName": "español (Latinoamérica)",
    },
    {"code": "zh", "name": "Chinese", "nativeName": "中文"},
    {"code": "cs", "name": "Czech", "nativeName": "česky"},
    {"code": "da", "name": "Danish", "nativeName": "dansk"},
    {"code": "en", "name": "English", "nativeName": "English (UK)"},
    {"code": "fi", "name": "Finnish", "nativeName": "suomi"},
    {"code": "fr-ca", "name": "French (Canada)", "nativeName": "français canadien"},
    {"code": "iw", "name": "Hebrew", "nativeName": "עברית"},
    {"code": "hu", "name": "Hungarian", "nativeName": "magyar"},
    {"code": "ko", "name": "Korean", "nativeName": "한국어"},
    {"code": "ms", "name": "Malay", "nativeName": "Bahasa Melayu"},
    {"code": "no", "name": "Norwegian", "nativeName": "norsk"},
    {"code": "sr", "name": "Serbian", "nativeName": "српски језик"},
    {"code": "sk", "name": "Slovak", "nativeName": "slovenčina"},
    {"code": "sv", "name": "Swedish", "nativeName": "svenska"},
    {"code": "tl", "name": "Tagalog", "nativeName": "Wikang Tagalog"},
    {"code": "th", "name": "Thai", "nativeName": "ไทย"},
    {"code": "uk", "name": "Ukrainian", "nativeName": "українська"},
    {"code": "vi", "name": "Vietnamese", "nativeName": "Tiếng Việt"},
    {"code": "fa", "name": "Persian", "nativeName": "فارسی"},
    {"code": "tr", "name": "Turkish", "nativeName": "Türkçe"},
]

languageEnglish2Code = {
    item["name"].lower(): item["code"] for item in availableTranslationLanguages
}
languageCode2English = {
    item["code"]: item["name"].lower() for item in availableTranslationLanguages
}
