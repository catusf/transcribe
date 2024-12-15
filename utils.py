import json
import os
import subprocess
from urllib.parse import urlparse

import pathvalidate
import requests
from pytube import YouTube

import platform


def is_windows():
    return platform.system() == "Windows"


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


def make_black_video_file(input_file, output_file, media_length):

    if is_windows():
        ff_path = os.path.join(".", "bin", "ffmpeg")
    else:
        ff_path = "ffmpeg"

    command = [
        ff_path,
        "-v",
        "quiet",  # No details shown
        "-y",  # Overwrite output files without asking
        "-f",
        "lavfi",  # Use lavfi to generate a video stream
        "-i",
        # Create a black video of 10 seconds, change the duration as needed
        f"color=c=black:s=640x360:d={media_length}",
        "-i",
        input_file,  # Input MP3 file
        "-crf",
        # Lower quality for smaller file size (range 0-51, where 0 is lossless)
        "28",
        "-c:v",
        "libx264",  # Use the H.264 codec for video
        "-c:a",
        "copy",  # Use the AAC codec for audio
        "-shortest",  # Ensure the video is the same length as the audio
        output_file,
    ]

    try:
        # Run the command using subprocess
        subprocess.run(command, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running:\n{' '.join(command)}")
        return False


def create_videos_for_all_mp3s(folder_path):
    """
    Create black video files for all MP3 files in a folder.

    Parameters:
    folder_path (str): Path to the folder containing MP3 files.
    """
    # Ensure the folder path is valid
    if not os.path.exists(folder_path) or not os.path.isdir(folder_path):
        print("The specified folder path does not exist or is not a directory.")
        return

    # Iterate over all files in the folder
    for filename in os.listdir(folder_path):
        if filename.lower().endswith(".mp3"):
            mp3_file_path = os.path.join(folder_path, filename)
            output_video_path = os.path.join(
                folder_path, f"{os.path.splitext(filename)[0]}.mp4"
            )
            json_meta = get_media_metadata(mp3_file_path)
            media_length = determine_media_length(json_meta)
            print(f"Processing {mp3_file_path}...")
            make_black_video_file(mp3_file_path, output_video_path, media_length)
            print(f"Created video: {output_video_path}")


def convert_media(input_file, output_file):
    # Get the path to the ffmpeg executable in the ./bin folder

    if is_windows():
        ff_path = os.path.join(".", "bin", "ffmpeg")
    else:
        ff_path = "ffmpeg"

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
        print(f"Error running:\n{' '.join(command)}")
        return False


def get_video_dimensions(json_meta):
    """
    Get the width and height of a video file from its metadata.

    Args:
        json_meta (dict): JSON metadata of the media file.

    Returns:
        tuple: A tuple containing:
            - width (int): Width of the video.
            - height (int): Height of the video.

        Returns (None, None) if no video stream is found.
    """
    streams = json_meta.get("streams", [])

    for stream in streams:
        if stream["codec_type"] == "video":
            width = stream.get("width")
            height = stream.get("height")
            return width, height

    return None, None  # No video stream found


def get_media_metadata(input_file):

    if is_windows():
        ff_path = os.path.join(".", "bin", "ffprobe")
    else:
        ff_path = "ffprobe"

    command = [
        ff_path,
        "-i",
        input_file,
        "-v",
        "quiet",
        "-print_format",
        "json",
        "-show_format",
        "-show_streams",
        "-hide_banner",
    ]

    # command.extend(
    #     "-v quiet -print_format json -show_format -show_streams -hide_banner".split(" ")
    # )

    metadata = subprocess.check_output(command)

    json_meta = json.loads(metadata)

    return json_meta


AUDIO_EXTENSIONS = {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a", ".wma"}

VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv", ".flv", ".wmv", ".webm", ".m4v"}

MEDIA_EXTENSIONS = AUDIO_EXTENSIONS | VIDEO_EXTENSIONS


def get_media_type(file_path):
    """
    Determine the media type of a file based on its extension.

    This function checks the file extension of the given file path and
    categorizes it as an audio file, a video file, or neither. It returns
    an integer code corresponding to the type of the file:

    - 0: The file is neither an audio nor a video file.
    - 1: The file is an audio file.
    - 2: The file is a video file.

    Parameters:
    file_path (str): The file path or name for which the media type is to be determined.

    Returns:
    int: An integer code indicating the media type of the file.
         0 if the file is neither an audio nor a video file.
         1 if the file is an audio file.
         2 if the file is a video file.

    Example:
    >>> get_media_type("example.mp3")
    1
    >>> get_media_type("example.mp4")
    2
    >>> get_media_type("example.txt")
    0
    """
    # Define audio and video file extensions

    # Extract the file extension
    file_extension = os.path.splitext(file_path)[1].lower()

    # Determine the media type
    if file_extension in AUDIO_EXTENSIONS:
        return 1  # Audio file
    elif file_extension in VIDEO_EXTENSIONS:
        return 2  # Video file
    else:
        return 0  # Not a media file


def determine_media_length(json_meta):
    return float(json_meta["format"]["duration"])


def determine_media_type(json_meta):
    """
    Determine if the media file is audio-only, video-only, or contains both.

    Args:
        json_meta (dict): JSON metadata of the media file.

    Returns:
        int:
            - 4 if the file contains both video and audio.
            - 2 if the file is video-only.
            - 1 if the file is audio-only.
            - 0 if the file has neither video nor audio streams.
    """
    streams = json_meta.get("streams", [])

    has_video = any(stream["codec_type"] == "video" for stream in streams)
    has_audio = any(stream["codec_type"] == "audio" for stream in streams)

    if has_video and has_audio:
        return 4  # File contains both video and audio
    elif has_video:
        return 2  # File is video-only
    elif has_audio:
        return 1  # File is audio-only
    else:
        return 0  # File has neither video nor audio streams


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
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    remaining_seconds = seconds % 60
    milliseconds = int((remaining_seconds % 1) * 1000)

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
