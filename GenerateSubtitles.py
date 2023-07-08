import speech_recognition as sr
from pydub import AudioSegment
import os
import re
import pysrt
import pinyin
import translators
from pathlib import Path

import glob

video_files = []

for file in glob.glob("*.mp4"):
    video_files.append(file)

subs_dir = "./subs"
Path(subs_dir).mkdir(parents=True, exist_ok=True)

# video_file = r"D:\Code\Playground\Subs\24 Peppa Pig Chinese -3DiMC6wWnc4-480pp-1688565567.mp4"

for video_file in video_files:
    print(f'Video file: {video_file}')
    path, filename = os.path.split(video_file)
    outpath = os.path.join(path, subs_dir)

    base_name = filename.split('.mp4')[0]
    audio_file = os.path.join(outpath, base_name +'.wav')
    sub_eng = os.path.join(outpath, base_name +'.en.srt')
    sub_vie = os.path.join(outpath, base_name +'.vi.srt')
    sub_zho = os.path.join(outpath, base_name +'.zh.srt')
    sub_pin = os.path.join(outpath, base_name +'.py.srt')
    sub_all = os.path.join(outpath, base_name +'.srt')

    no_text = "^[0-9\n\r]"


    # Load the video file
    video = AudioSegment.from_file(video_file, format="mp4")
    audio = video.set_channels(1).set_frame_rate(16000).set_sample_width(2)
    audio.export(audio_file, format="wav")

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

    result = r.recognize_whisper(audio_text, show_dict=True, language='chinese', word_timestamps=True) #translate=True, 

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

        subs.save(sub_zho)

        print(f'Subtitle written {sub_zho}')


    with open(sub_zho, "r", encoding='utf-8') as file_zh:
        text_zh = file_zh.readlines() 
        
        count = len(text_zh)

        text_all = ''
        text_eng = ''
        text_vie = ''
        text_pin = ''

        for line in text_zh:
            if re.match(no_text, line): # Timing and count lines
                text_all += line
                text_eng += line
                text_vie += line
                text_pin += line
            else:
                eng = translators.translate_text(line, translator='bing', from_language='zh', to_language='en') + '\n'
                pin = pinyin.get(line, delimiter=' ')
                vie = translators.translate_text(line, translator='bing', from_language='zh', to_language='vi') + '\n'
                print(f'{line}\t{pin}\t{eng}\t{vie}')

                text_all += pin
                text_all += line
                text_all += vie

                text_eng += eng
                text_pin += pin
                text_vie += vie

        with open(sub_all, "w", encoding='utf-8') as file:
            file.write(text_all)
        
        with open(sub_eng, "w", encoding='utf-8') as file:
            file.write(text_eng)
        
        with open(sub_vie, "w", encoding='utf-8') as file:
            file.write(text_vie)

        with open(sub_pin, "w", encoding='utf-8') as file:
            file.write(text_pin)

        print(f'Combined file written {sub_all}')



'''
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip

sub_files = [sub_en, sub_zh, sub_py]
vid_files = [video_file]

suffix = ['Sub1', 'Sub2', 'Sub3']

fonts = ['arial.ttf', 'simhei.ttf', 'arial.ttf']
video_height = 480
video_width = 854
subtitle_x_position = 'center'

y_positions = [video_height* 4.5 / 5, video_height* 4.2 / 5, video_height* 3.9 / 5]

colors = ['white', 'blue', 'green']

for i, sub_file in enumerate(sub_files):
    generator = lambda txt: TextClip(txt, font=fonts[i], fontsize=24, color=colors[i])

    subs = SubtitlesClip(sub_file, generator)
    subtitles = SubtitlesClip(subs, generator)

    video = VideoFileClip(vid_files[-1])
    
    subtitle_y_position = y_positions[i]

    text_position = (subtitle_x_position, subtitle_y_position)

# subtitle_clips.append(text_clip.set_position(text_position))

# # result = CompositeVideoClip([video, subtitles.set_pos(('center','bottom'))])

    result = CompositeVideoClip([video, subtitles.set_pos(text_position)])

    output_file = f'{base_name}.{suffix[i]}.mp4'

    result.write_videofile(output_file)

    vid_files.append(output_file)

'''