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
from datetime import datetime

import json

CONFIG_FILE = 'CONFIG.json'

CONFIGS = {}

try:
    with open(CONFIG_FILE, "r") as read_file:
        CONFIGS = json.load(read_file)
except Exception as ex:
    print(ex)

if not CONFIGS:
    CONFIGS = {
        'VIDEO_DIR' : 'C:/Users/it.fsoft/Downloads',
        'SUBTITLE_DIR' : './downloads/subs',
    }

# try:
#     with open(CONFIG_FILE, "w") as read_file:
#         json.dump(CONFIGS, read_file)
# except Exception as ex:
#     print(ex)

SUBTITLE_DIR = CONFIGS['SUBTITLE_DIR']
os.makedirs(SUBTITLE_DIR, exist_ok=True)

WAITING_NEW_FILE = 5

while True:
    sub_files = []

    sub_eng = ''
    sub_vie = ''
    sub_zho = ''
    sub_pin = ''
    sub_all = ''

    patterns = f'{SUBTITLE_DIR}/*.zh.srt'
    for file in glob.glob(patterns):
        sub_zho = file
        # print(f'Chinese sub file: {sub_zho}')
        path, filename = os.path.split(sub_zho)
        outpath = path

        base_name = filename.split('.zh.srt')[0]
        sub_eng = os.path.join(outpath, base_name +'.en.srt')
        sub_vie = os.path.join(outpath, base_name +'.vi.srt')
        sub_zho = os.path.join(outpath, base_name +'.zh.srt')
        sub_pin = os.path.join(outpath, base_name +'.py.srt')
        sub_all = os.path.join(outpath, base_name +'.srt')

        # Sets vars to None if files exist
        if not (os.path.exists(sub_eng) and os.path.exists(sub_vie) and os.path.exists(sub_pin)):
            sub_files.append(sub_zho)
            break

    if not sub_files:
        #print(f'{datetime.now()} > No subtitle files. Waiting for {WAITING_NEW_FILE}s')
        time.sleep(WAITING_NEW_FILE)

        continue

    print(f'Start translating {sub_zho}...')

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

        NORMAL_MAX_TRANS = 100
        COMBINED_TRANS = NORMAL_MAX_TRANS

        TEXT_ITEMS = len(text_translate)
        batches = round((TEXT_ITEMS / NORMAL_MAX_TRANS*1.0) + 0.5)
        remaining = len(text_translate)

        for b in range(batches):
            text_range = text_translate[b*NORMAL_MAX_TRANS:(b+1)*NORMAL_MAX_TRANS]
            index_range = index_translate[b*NORMAL_MAX_TRANS:(b+1)*NORMAL_MAX_TRANS]
            length = len(text_range)

            combined_text = ''.join(text_range)

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
                    expanded_pin = pin.split(SEPERATOR)

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
            for x in range(min(NORMAL_MAX_TRANS, TEXT_ITEMS-b*NORMAL_MAX_TRANS)):
                y = index_translate[b*NORMAL_MAX_TRANS+x]
                text_eng[y] = expanded_eng[count] + '\n'
                text_vie[y] = expanded_vie[count] + '\n'
                text_pin[y] = expanded_pin[count].strip() + '\n'
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




