import speech_recognition as sr
# from pydub import AudioSegment
import os
import re
import pysrt
import pinyin
# import translators
from pathlib import Path
import glob
import shutil
import shlex

import subprocess
import json

SUB_CLIP_DURATION = 600 # 300s or 5 min
SPLIT_VIDEO = False

VIDEO_DIR = "./downloads"
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

if SPLIT_VIDEO:
    video_files = []

    for file in glob.glob("*.mp4"):
        video_files.append(file)

    # Split videos into shorter clips
    for video_file in video_files:
        if video_file.find(' '):
            new_video_file = video_file.replace(' ', '')

        shutil.move(video_file, new_video_file)

    video_files = []

    for file in glob.glob("*.mp4"):
        video_files.append(file)

    video_files.sort()

    
    Path(SUBTITLE_DIR).mkdir(parents=True, exist_ok=True)

    from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip

    # Split videos into shorter clips
    for video_file in video_files:
        
        base_name = video_file.split('.mp4')[0]
        path, filename = os.path.split(video_file)
        new_path = os.path.join(path, SUBTITLE_DIR)

        length = movie_duration(video_file)
        movie_resolution(video_file)

        if length < SUB_CLIP_DURATION/60*1.1:
            print(f'Video short enought {video_file}')
            continue
            
        starttime = 0
        count = 1

        while starttime < length:
            endtime = starttime + SUB_CLIP_DURATION
            targetname='%s-%s-%02i.mp4' % (base_name, f'{int(SUB_CLIP_DURATION/60)}min', count)

            ffmpeg_extract_subclip(video_file, starttime, endtime, targetname=targetname)
            
            count += 1
            starttime += SUB_CLIP_DURATION

        shutil.move(video_file, new_path)

video_files = []

for file in glob.glob(f"{VIDEO_DIR}/*.mp4"):
    video_files.append(file)

for video_file in video_files:
    if video_file.find(' '):
        new_video_file = video_file.replace(' ', '')
    try:
        shutil.move(video_file, new_video_file)
    except Exception as ex:
        print(ex)

video_files = []

for file in glob.glob(f"{VIDEO_DIR}/*.mp4"):
    video_files.append(file)

video_files.sort()

while video_files:
    video_file = video_files.pop(0)

    print(f'Video file: {video_file}')
    path, filename = os.path.split(video_file)
    outpath = SUBTITLE_DIR

    base_name = filename.split('.mp4')[0]
    audio_file = os.path.join(outpath, base_name +'.wav')
    new_video_file = os.path.join(outpath, base_name +'.mp4')
    sub_eng = os.path.join(outpath, base_name +'.en.srt')
    sub_vie = os.path.join(outpath, base_name +'.vi.srt')
    sub_zho = os.path.join(outpath, base_name +'.zh.srt')
    sub_pin = os.path.join(outpath, base_name +'.py.srt')
    sub_all = os.path.join(outpath, base_name +'.srt')

    no_text = "^[0-9\n\r]"

    # Load the video file
    # video = AudioSegment.from_file(video_file, format="mp4")
    # audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    # audio.export(audio_file, format="wav")
#-v quiet 
    cmd_str = f'ffmpeg -v quiet -i "{video_file}" "{audio_file}"'
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

    print(f'Starting transcribing... {audio_file}')

    result = r.recognize_whisper(audio_text, show_dict=True, language='chinese', word_timestamps=True) #translate=True, 

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
   
    if not video_files:
        for file in glob.glob(f"{VIDEO_DIR}/*.mp4"):
            video_files.append(file)

        for video_file in video_files:
            if video_file.find(' '):
                new_video_file = video_file.replace(' ', '')

            shutil.move(video_file, new_video_file) 

        video_files.sort()

        if not video_files:
            print('All videos processed')
            break


