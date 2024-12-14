#!/usr/bin/env python3

import os
import subprocess
import re
import argparse
from pathvalidate import sanitize_filename
from openpyxl import Workbook
from datetime import datetime, timedelta


def is_colab():
    try:
        import google.colab

        return True
    except ImportError:
        return False


# Define the directory containing the media files
COLAB_MEDIA_DIR = "/content/drive/My Drive/ChatGPT/transcribe/subs"

# Constants
MEDIA_FOLDER = COLAB_MEDIA_DIR if is_colab() else "./downloads/subs"

TIME_STAMP_FORMAT = "%H:%M:%S.%f"
OFFSET_LEFT_MS = 700
OFFSET_RIGHT_MS = 100

# MEDIA_FOLDER = "downloads/subs"
OUT_MEDIA = "videos-out"

SPLIT_VIDEOS = True

TRIM_VIDEOS = False

SPLIT_REPORT = 50

DEBUG_NOW = True
MAX_DEBUG = 2000000
MAX_FILENAME_LENGTH = 100


def parse_time(time_str):
    hours, minutes, seconds = time_str.split(":")
    seconds, milliseconds = seconds.split(".")
    return timedelta(
        hours=int(hours),
        minutes=int(minutes),
        seconds=int(seconds),
        milliseconds=int(milliseconds),
    )


def split_video(video_file, srt_file, report_data):
    """
    Splits the video into multiple segments based on the timestamps provided in the .srt file.

    Parameters:
    video_file (str): Path to the video file.
    srt_file (str): Path to the corresponding .srt subtitle file.
    report_data (list): List to collect reporting information.
    translator (Translator): Google Translator instance.
    """
    # Read the .srt file
    with open(srt_file, "r", encoding="utf-8") as f:
        text = f.read()

    path, filename = os.path.split(video_file)
    filebase, fileext = os.path.splitext(filename)
    new_dir = os.path.join(path, filebase)
    os.makedirs(new_dir, exist_ok=True)

    # Define the improved regular expression with capturing groups
    regex = r"(?m)^(\d+)$\n^(\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3})$\n((?:(?!^\d+$).*\n?)+)"

    # # Read the content from the text file
    # with open('input.txt', 'r', encoding='utf-8') as file:
    #     text = file.read()

    # Find all matches
    text = text.replace("（", "(").replace("）", ")").replace(" )", ")")
    matches = re.finditer(regex, text)

    # Iterate through all matches and print their captured groups
    for num, match in enumerate(matches, start=1):

        if DEBUG_NOW and num > MAX_DEBUG:
            break

        index = int(match.group(1))

        if index % SPLIT_REPORT == 0:
            print(f"Processed {index} records")

        timestamp = match.group(2).strip()
        text_content = match.group(3).strip()
        # Parse subtitle lines

        # index = 1
        # for i in range(0, len(lines), 4):  # Assuming each subtitle block has 4 lines
        #     # Ensure valid subtitle format and lines are not empty
        #     if len(lines[i+1].strip()) > 0 and len(lines[i+2].strip()) > 0:
        start, end = parse_srt_timestamp(timestamp)

        end += timedelta(milliseconds=OFFSET_RIGHT_MS)
        # start = start0 - timedelta(milliseconds=OFFSET_LEFT_MS)

        # if start.time() > start0.time():
        #     start = datetime(1900, 1, 1, 0, 0, 0)  # zero_time

        # text = lines[i+2].strip()
        # Extract English and Chinese parts from text
        items = parse_text(text_content)
        chinese_text, pinyin_text, english_text = (
            items[0],
            items[1] if len(items) > 1 else "",
            items[2] if len(items) > 2 else "",
        )
        sanitized_text = sanitize_filename(
            f"{chinese_text}_{pinyin_text}_{english_text}".replace(" )", ")").replace(
                " ", "-"
            )
        )  # Replace spaces with underscores

        output_file = f"{index:03d}_{sanitized_text[:MAX_FILENAME_LENGTH]}{fileext}"
        output_file = os.path.join(new_dir, output_file)

        if SPLIT_VIDEOS:

            # Split video using ffmpeg with error handling
            try:
                cmd = [
                    "ffmpeg",
                    "-loglevel",
                    "error",
                    "-y",
                    "-i",
                    video_file,
                    "-ss",
                    timestamp_string(start),
                    "-to",
                    timestamp_string(end),
                    "-c",
                    "copy",
                    output_file,
                ]
                # print("Command: %s" % " ".join(cmd))
                subprocess.run(
                    cmd,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.PIPE,
                    check=True,
                )
            except subprocess.CalledProcessError as e:
                # Print error details
                print(
                    f"Error splitting video segment {index}: {e.stderr.decode('utf-8').strip()}"
                )
                continue

        # Get the length of the segment
        length = (end - start).total_seconds()

        # Append report data
        report_data.append(
            [
                video_file,
                index,
                chinese_text,
                english_text,
                output_file,
                length,
                "",
                "",
            ]
        )
    pass


def parse_srt_timestamp(srt_line):
    """
    Parses a timestamp line from an .srt file and converts it to a format compatible with ffmpeg.

    Parameters:
    srt_line (str): A line from the .srt file containing the start and end timestamps.

    Returns:
    tuple: A tuple containing the start and end timestamps in ffmpeg-compatible format.
    """
    # Example timestamp format: "00:00:10,000 --> 00:00:15,000"
    start, end = srt_line.strip().split(" --> ")
    # Convert to ffmpeg-compatible format: "HH:MM:SS"
    start = start.replace(",", ".")
    end = end.replace(",", ".")

    return datetime.strptime(start, TIME_STAMP_FORMAT), datetime.strptime(
        end, TIME_STAMP_FORMAT
    )


def timestamp_string(time_value):
    return time_value.strftime(TIME_STAMP_FORMAT)


def parse_text(text):
    """
    Parses the subtitle text to extract English and Chinese parts.

    Parameters:
    text (str): The text line from the .srt file containing both English and Chinese.

    Returns:
    tuple: A list containing the Chinese + Pinyin + English text.
    """
    return [item.strip() for item in text.split("\n")]


def generate_report(report_data, output_filename="video_split_report.xlsx"):
    """
    Generates an Excel report from the report data.

    Parameters:
    report_data (list): List containing the report information.
    output_filename (str): Name of the output Excel file.
    """
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = "Video Report"

    # Write header row
    headers = [
        "Input Filename",
        "Index",
        "Chinese Text",
        "English Text",
        "Filename",
        "Length",
        "Vietnamese from English",
        "Vietnamese from Chinese",
    ]
    sheet.append(headers)

    # Write data rows
    for row in report_data:
        sheet.append(row)

    # Save the workbook
    workbook.save(output_filename)
    print(f"Report generated: {output_filename}")


def main():
    # Argument parser to handle input file
    parser = argparse.ArgumentParser(
        description="Split and trim a video based on SRT subtitles."
    )
    parser.add_argument(
        "input_file",
        nargs="?",
        default="吃饭_｜_Chinese_Daily_Dialogues_｜_Upper_Beginner_｜_Chinese_Listening_Practice_HSK_3⧸4.webm",  # "input.webm",
        help="Input video file (default is 'input.mp4')",
    )

    args = parser.parse_args()

    import shutil
    from pathvalidate import sanitize_filename

    file = args.input_file
    orgfilepathbase, orgfilext = os.path.splitext(file)
    input_file = os.path.join(MEDIA_FOLDER, sanitize_filename(file).replace(" ", "_"))
    shutil.move(os.path.join(MEDIA_FOLDER, file), input_file)
    filepathbase, filext = os.path.splitext(input_file)
    srt_file = filepathbase + ".srt"
    shutil.move(os.path.join(MEDIA_FOLDER, orgfilepathbase + ".srt"), srt_file)

    # print(input_file)
    print(srt_file)

    report_data = []

    if os.path.exists(srt_file):
        print(f"Splitting {input_file} using {srt_file}")
        split_video(input_file, srt_file, report_data)

        # Generate report
        report_file = filepathbase + ".xlsx"
        generate_report(report_data, report_file)
    else:
        print(f"No corresponding .srt file found for {input_file}")

    print("All videos processed!")


# Example usage: main()
if __name__ == "__main__":
    main()
