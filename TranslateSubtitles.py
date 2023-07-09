import speech_recognition as sr
from pydub import AudioSegment
import os
import re
import pysrt
import pinyin
import translators
from pathlib import Path
import glob
import shutil
import shlex

import subprocess
import json


SUBTITLE_DIR = "./subs/"
Path(SUBTITLE_DIR).mkdir(parents=True, exist_ok=True)

# video_file = r"D:\Code\Playground\Subs\24 Peppa Pig Chinese -3DiMC6wWnc4-480pp-1688565567.mp4"
'''
import argostranslate.package
import argostranslate.translate

from_code = "zh"
to_code = "en"

# Download and install Argos Translate package
argostranslate.package.update_package_index()
available_packages = argostranslate.package.get_available_packages()
package_to_install = next(
    filter(
        lambda x: x.from_code == from_code and x.to_code == to_code, available_packages
    )
)
argostranslate.package.install_from_path(package_to_install.download())

# Translate
translatedText = argostranslate.translate.translate("每个人都有他的作战策略，直到脸上中了一拳。这首歌使我想起了我年轻的时候。", from_code, to_code)
print(translatedText)
# '¡Hola Mundo!'
'''

sub_files = []

for file in glob.glob(f'{SUBTITLE_DIR}*.zh.srt'):
    sub_files.append(file)

print(f'Chinese subtitle files {"|".join(sub_files)}')

sub_files.sort()

for sub_zho in sub_files:
    print(f'Chinese sub file: {sub_zho}')
    path, filename = os.path.split(sub_zho)
    outpath = path

    base_name = filename.split('.zh.srt')[0]
    sub_eng = os.path.join(outpath, base_name +'.en.srt')
    sub_vie = os.path.join(outpath, base_name +'.vi.srt')
    sub_zho = os.path.join(outpath, base_name +'.zh.srt')
    sub_pin = os.path.join(outpath, base_name +'.py.srt')
    sub_all = os.path.join(outpath, base_name +'.srt')

    # Sets vars to None if files exist
    if os.path.exists(sub_eng):
        sub_eng = None
    if os.path.exists(sub_vie):
        sub_vie = None
    if os.path.exists(sub_pin):
        sub_pin = None

    # Pattern for number
    NO_SUBTILE_TEXT = "^[0-9\n\r]"

    with open(sub_zho, "r", encoding='utf-8') as file_zh:
        text_zh = file_zh.readlines() 
        
        count = len(text_zh)

        text_all = ''
        text_eng = ''
        text_vie = ''
        text_pin = ''

        for line in text_zh:
            if re.match(NO_SUBTILE_TEXT, line): # Timing and count lines
                text_all += line
                text_eng += line
                text_vie += line
                text_pin += line
            else:
                if sub_eng: # If file not exists
                    eng = translators.translate_text(line, translator='google', from_language='zh', to_language='en') + '\n'

                if sub_pin: # If file not exists
                    pin = pinyin.get(line, delimiter=' ')

                if sub_vie: # If file not exists
                    vie = translators.translate_text(line, translator='google', from_language='zh', to_language='vi') + '\n'

                print(f'{line}\t{pin}\t{eng}\t{vie}')

                text_all += pin
                text_all += line
                text_all += vie

                text_eng += eng
                text_pin += pin
                text_vie += vie

        if sub_eng:
            with open(sub_eng, "w", encoding='utf-8') as file:
                file.write(text_eng)

        if sub_vie:        
            with open(sub_vie, "w", encoding='utf-8') as file:
                file.write(text_vie)

        if sub_pin:
            with open(sub_pin, "w", encoding='utf-8') as file:
                file.write(text_pin)

        if sub_eng and sub_vie and sub_pin:
            with open(sub_all, "w", encoding='utf-8') as file:
                file.write(text_all)

            print(f'Combined file written {sub_all}')

