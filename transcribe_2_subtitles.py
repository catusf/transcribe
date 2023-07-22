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

SUB_CLIP_DURATION = 600 # 300s or 5 min
SPLIT_VIDEO = False

VIDEO_DIR = "C:/Users/Dan/Downloads"
SUBTITLE_DIR = "./downloads/subs"

# video_file = r"D:\Code\Playground\Subs\24 Peppa Pig Chinese -3DiMC6wWnc4-480pp-1688565567.mp4"

''' Get video file's first stream's width and height

    Requires ffmpeg installed
'''
def movie_resolution(input_file):
    cmds = f"ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 -print_format json -i".split(" ")
    cmds.append(f'"input_file"')
    print(cmds)
    metadata = subprocess.check_output(cmds)

    metadata = json.loads(metadata)
    stream0 = metadata['streams'][0]
    width, height = stream0['width'], stream0['height']
    print(metadata)

    return width, height

''' Get video file's duration

    Requires ffmpeg installed
'''
def movie_duration(input_file):
    cmds = f"ffprobe -v quiet -print_format json -show_format -hide_banner -i".split(" ")
    cmds.append(f'"input_file"')
    print(cmds)
    metadata = subprocess.check_output(cmds)

    metadata = json.loads(metadata)
    length = float(metadata['format']['duration'])
    print(metadata)

    return length

WAITING_NEW_FILE = 5

# datetime object containing current date and time
 
while True:
    video_files = []

    for video_file in glob.glob(f"{VIDEO_DIR}/*.mp4"):
        if not pathvalidate.is_valid_filepath(video_file):
            new_video_file = pathvalidate.sanitize_filepath(video_file)
            new_video_file = new_video_file.replace(" ", "_")
        try:
            shutil.move(video_file, new_video_file)
            video_file = new_video_file
        except Exception as ex:
            print(ex)
            
        video_files.append(video_file)
        break
    
    if not video_files:
        print(f'{datetime.now()} > No video files. Waiting for {WAITING_NEW_FILE}s.')
        time.sleep(WAITING_NEW_FILE)
        
        continue
    
    video_file = video_files.pop()

    print(f'Start transcribing {video_file}...')
    
    path, filename = os.path.split(video_file)
    outpath = SUBTITLE_DIR

    base_name = filename.split('.mp4')[0]
    audio_file = os.path.join(outpath, base_name +'.wav')
    new_video_file = os.path.join(outpath, base_name +'.mp4')
    sub_zho = os.path.join(outpath, base_name +'.zh.srt')

    no_text = "^[0-9\n\r]"

    cmd_str = f'ffmpeg -v quiet -y -i "{video_file}" "{audio_file}"'
    print(cmd_str)
    cmds = cmd_str.split(" ")
    print(cmds)
    # metadata = subprocess.check_output(cmds)
    os.system(cmd_str)

    shutil.move(video_file, new_video_file)

    print(f'Audio file exported {audio_file}')

    # Initialize recognizer class (for recognizing the speech)
    r = sr.Recognizer()

    # Open the audio file
    with sr.AudioFile(audio_file) as source:
        audio_text = r.record(source)
    # Recognize the speech in the audio

    translations = [False]
    languages = ['zh']
    sub_files = [sub_zho]

    print(f'Starting processing {audio_file}...')

    result = r.recognize_whisper(audio_text, show_dict=True, language='chinese', word_timestamps=True) #translate=True, 
    os.remove(audio_file)
    print(f' done.')

    subs = pysrt.SubRipFile()
    sub_idx = 1
    for i in range(len(result["segments"])):
        start_time = result["segments"][i]["start"]
        end_time = result["segments"][i]["end"]
        duration = end_time - start_time
        timestamp = f"{start_time:.3f} - {end_time:.3f}"
        text = result["segments"][i]["text"]

        sub = pysrt.SubRipItem(index=sub_idx, start=pysrt.SubRipTime(seconds=start_time), end=pysrt.SubRipTime(seconds=end_time), text=text)
        subs.append(sub)
        sub_idx += 1

    if not subs:
        print(f'Subtitle empty {sub_zho}')
    
    else:
        subs.save(sub_zho)

        print(f'Subtitle written {sub_zho}')



