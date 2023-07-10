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
import time


SUBTITLE_DIR = "./subs/"
Path(SUBTITLE_DIR).mkdir(parents=True, exist_ok=True)

'''
from transformers import MarianMTModel, MarianTokenizer
from typing import Sequence

class Translator:
    def __init__(self, source_lang: str, dest_lang: str) -> None:
        self.model_name = f'Helsinki-NLP/opus-mt-{source_lang}-{dest_lang}'
        self.model = MarianMTModel.from_pretrained(self.model_name)
        self.tokenizer = MarianTokenizer.from_pretrained(self.model_name)
        
    def translate(self, texts: Sequence[str]) -> Sequence[str]:
        tokens = self.tokenizer(list(texts), return_tensors="pt", padding=True)
        translate_tokens = self.model.generate(**tokens,max_length= 60)
        return [self.tokenizer.decode(t, skip_special_tokens=True) for t in translate_tokens]
        

marian_zh_en = Translator('zh', 'en')
print(marian_zh_en.translate(['还在笑眼睛不要了.']))

marian_zh_vi = Translator('zh', 'vi')
print(marian_zh_vi.translate(['还在笑眼睛不要了.']))
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

    if (not sub_eng) or (not sub_vie) or (not sub_pin):
        continue

    # Pattern for number
    NO_SUBTILE_TEXT = "^[0-9\n\r]"

    with open(sub_zho, "r", encoding='utf-8') as file_zh:
        text_zh = file_zh.readlines() 
        
        text_all = ''
        text_eng = ''
        text_vie = ''
        text_pin = ''

        count = 1
        MAX_TRANS = 50
        SLEEP_ONE = 0.5
        SLEEP_BATCH = 20
        
        for line in text_zh:
            
            if re.match(NO_SUBTILE_TEXT, line): # Timing and count lines
                text_all += line
                text_eng += line
                text_vie += line
                text_pin += line
            else:
                count += 1
                if sub_eng: # If file not exists
#                    eng = marian_zh_en.translate(line)[0] + '\n'
                    eng = translators.translate_text(line, translator='bing', from_language='zh', to_language='en') + '\n'
                    text_eng += eng
                    time.sleep(SLEEP_ONE)

                if sub_vie: # If file not exists
#                    vie = marian_zh_vi.translate(line)[0] + '\n'
                    vie = translators.translate_text(line, translator='google', from_language='zh', to_language='vi') + '\n'
                    text_vie += vie

                if sub_pin: # If file not exists
                    pin = pinyin.get(line, delimiter=' ')
                    text_pin += pin

                if sub_eng and sub_vie and sub_pin:
                    print(f'{line}\t{pin}\t{eng}\t{vie}')

                    text_all += pin
                    text_all += line
                    text_all += vie

            if not count % MAX_TRANS:
                time.sleep(SLEEP_BATCH)
                

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

