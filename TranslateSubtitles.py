import speech_recognition as sr
#from pydub import AudioSegment
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

VIDEO_DIR = ".downloads/"

SUBTITLE_DIR = "./downloads/subs/"
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

sub_files.sort(reverse=True)

print(f'Chinese subtitle files {"|".join(sub_files)}')

while sub_files:
    sub_zho = sub_files.pop()
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
        
        text_all = text_zh.copy()
        text_pin = text_zh.copy()
        text_eng = text_zh.copy()
        text_vie = text_zh.copy()

        count = 1
        MAX_TRANS = 50
        SLEEP_ONE = 1
        SLEEP_BATCH = 60
        SEPERATOR = '\n'
        
        index_translate = []
        text_translate = []

        for i, line in enumerate(text_zh):            
            if not re.match(NO_SUBTILE_TEXT, line): # Timing and count lines
                index_translate.append(i)
                text_translate.append(line)
        
        # _ = translators.preaccelerate_and_speedtest()  # Optional. Caching sessions in advance, which can help improve access speed.

        COMBINED_TRANS = min(100, len(text_translate))

        for i, item in enumerate(index_translate):
            if not (i + 1) % COMBINED_TRANS:
                combined_text = ''.join(text_translate[i - COMBINED_TRANS + 1 : i + 1])

                error_count = 0
                sleep = SLEEP_BATCH
                sleep_one = SLEEP_ONE

                while error_count < 5:
                    try:
                        eng = translators.translate_text(combined_text, translator='baidu', from_language='zh', to_language='en')
                        expanded_eng = eng.split(SEPERATOR)
                        print(f'Sleeping {sleep_one}s')
                        time.sleep(sleep_one)
                        vie = translators.translate_text(combined_text, translator='baidu', from_language='zh', to_language='vie')
                        expanded_vie = vie.split(SEPERATOR)
                        pin = pinyin.get(combined_text, delimiter=' ')
                        expanded_pin = pin.split(SEPERATOR)[:-1]

                        break # no need to loop when succeeds
                    except Exception as ex:
                        print(ex)
                        error_count += 1
                        print(f'Sleeping {sleep}s')
                        time.sleep(sleep)

                        sleep = sleep * 1.5
                        sleep_one = sleep * 1.5

                print(f'===={combined_text}\n----{pin}\n----{eng}\n---{vie}')

                count = 0
                for x in range(i - COMBINED_TRANS + 1, i + 1):
                    y = index_translate[x]
                    text_eng[y] = expanded_eng[count] + '\n'
                    text_vie[y] = expanded_vie[count] + '\n'
                    text_pin[y] = expanded_pin[count] + '\n'
                    text_all[y] = text_zh[y] + text_pin[y] + text_vie[y]
                    count += 1

            # if i and not i % MAX_TRANS:
            #     time.sleep(SLEEP_BATCH)

        with open(sub_eng, "w", encoding='utf-8') as file:
            file.write(''.join(text_eng))

        with open(sub_vie, "w", encoding='utf-8') as file:
            file.write(''.join(text_vie))

        with open(sub_pin, "w", encoding='utf-8') as file:
            file.write(''.join(text_pin))

        with open(sub_all, "w", encoding='utf-8') as file:
                file.write(''.join(text_all))

        print(f'Combined file written {sub_all}')                    

    if not sub_files:
        for file in glob.glob(f'{SUBTITLE_DIR}*.zh.srt'):
            sub_files.append(file)

        sub_files.sort(reverse=True)

        if not sub_files: # Nothing to translate
            break




