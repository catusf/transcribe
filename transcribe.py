#!/usr/bin/env python3

import glob
import os
import re
import shutil
import time
import json
from transformers import M2M100ForConditionalGeneration, M2M100Tokenizer

# from google.colab import drive

# import pinyin
import pinyin_jyutping
import pysrt
import speech_recognition as sr
import translators
import chinese_converter

from utils import *

pinyin_generator = pinyin_jyutping.PinyinJyutping()

SEPARATOR = "\n"


def is_colab():
    try:
        import google.colab

        return True
    except ImportError:
        return False


# Define the directory containing the media files
COLAB_MEDIA_DIR = "/content/drive/My Drive/trans"

# Constants
MEDIA_DIR = COLAB_MEDIA_DIR if is_colab() else "./downloads"

LANGUAGE = "chinese"
DEST_LANGUAGE_1 = "vietnamese"
DEST_LANGUAGE_2 = "english"

URL_FILE = os.path.join(MEDIA_DIR, "urls.txt")
SUBTITLE_DIR = os.path.join(MEDIA_DIR, "subs")
DONE_SUBS_DIR = os.path.join(SUBTITLE_DIR, "done")

os.makedirs(DONE_SUBS_DIR, exist_ok=True)

TRANSLATOR_SERVICE = (
    # "bing"  #
    # "alibaba"  #
    # "baidu"
    "google"  # Define the default translator service here
)

# Define local directory to save the model
MODEL_DIR = "./downloads/m2m100_model"
LOADED_MODEL = False

CACHE_FILE = os.path.join(MEDIA_DIR, "translation_cache.json")


def no_current(dir):
    return "." + dir.removeprefix(MEDIA_DIR)


def initial_checks():
    """
    Perform initial setup checks and create necessary directories and files.
    """
    os.makedirs(SUBTITLE_DIR, exist_ok=True)
    if not os.path.exists(URL_FILE):
        with open(URL_FILE, "w", encoding="utf-8") as file:
            file.write(
                "# URLs to download. If needed, add a tab character and the filename.\n"
            )


def load_translation_cache():
    """
    Load translation cache from a JSON file.
    """
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r", encoding="utf-8") as file:
            return json.load(file)
    else:
        save_translation_cache({})
        return {}


def save_translation_cache(cache):
    """
    Save translation cache to a JSON file.
    """
    with open(CACHE_FILE, "w", encoding="utf-8") as file:
        json.dump(cache, file, ensure_ascii=False, indent=4)


# Function to set up the model and tokenizer
def setup_model(MODEL_DIR):
    """
    Sets up the translation model and tokenizer. Loads them from the local directory if available,
    otherwise downloads them and saves them locally.

    Parameters:
    MODEL_DIR (str): The directory where the model and tokenizer are saved.

    Returns:
    model (M2M100ForConditionalGeneration): The translation model.
    tokenizer (M2M100Tokenizer): The tokenizer for the model.
    """
    global LOADED_MODEL

    if LOADED_MODEL:
        print("Offline translation model loaded already.")
        return model, tokenizer

    print("Loading offline translation model...")

    if not os.path.exists(MODEL_DIR):
        # Load the model and tokenizer from Hugging Face
        print(f"Downloading and saving the model and tokenizer to {MODEL_DIR}")
        model = M2M100ForConditionalGeneration.from_pretrained("facebook/m2m100_418M")
        tokenizer = M2M100Tokenizer.from_pretrained("facebook/m2m100_418M")

        # Save model and tokenizer locally
        model.save_pretrained(MODEL_DIR)
        tokenizer.save_pretrained(MODEL_DIR)
        print(f"Model and tokenizer saved locally at {MODEL_DIR}")
    else:
        # Load the model and tokenizer from the local directory
        print(f"Loading model and tokenizer from {MODEL_DIR}")
        model = M2M100ForConditionalGeneration.from_pretrained(MODEL_DIR)
        tokenizer = M2M100Tokenizer.from_pretrained(MODEL_DIR)

    print("Offline translation model loaded.")

    LOADED_MODEL = True
    return model, tokenizer


model, tokenizer = None, None


# Function to perform the translation
def offline_translate(raw_text, from_lang, to_lang):
    """
    Translates text from one language to another using a pre-loaded model and tokenizer.

    Parameters:
    model (M2M100ForConditionalGeneration): The translation model
    tokenizer (M2M100Tokenizer): The tokenizer for the model
    text (str): The input text to translate
    from_lang (str): The source language code (e.g., 'hi', 'zh')
    to_lang (str): The target language code (e.g., 'fr', 'en')

    Returns:
    str: The translated text
    """
    # Set the source language
    global model, tokenizer
    model, tokenizer = setup_model(MODEL_DIR)
    tokenizer.src_lang = from_lang

    text_array = raw_text.strip().split(SEPARATOR)
    translated_text_array = []

    for text in text_array:
        # Tokenize the input text
        encoded_text = tokenizer(text, return_tensors="pt")

        # Generate the translation by setting the forced beginning of the sentence to the target language
        generated_tokens = model.generate(
            **encoded_text, forced_bos_token_id=tokenizer.get_lang_id(to_lang)
        )

        # Decode the translated tokens to get the output text
        translated_text_array.append(
            tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
        )

    return SEPARATOR.join(translated_text_array)


def translate_with_cache(text, translator, srclang, destlang, cache):
    """
    Translate text with caching to avoid repeated translations.
    """
    cache_key = f"{srclang}_{destlang}_{text}"
    if cache_key in cache:
        return True, cache[cache_key]
    else:
        translation = translators.translate_text(
            text, translator=translator, from_language=srclang, to_language=destlang
        )
        translation = translation.replace("\n ", "\n")
        cache[cache_key] = translation
        return False, translation


def translate_offline_with_cache(text, srclang, destlang, cache):
    """
    Translate text with caching to avoid repeated translations.
    """
    cache_key = f"{srclang}_{destlang}_{text}"
    if cache_key in cache:
        return True, cache[cache_key]
    else:
        translation = offline_translate(text, srclang, destlang)
        # translators.translate_text(
        #     text, translator=translator, from_language=srclang, to_language=destlang
        # )

        cache[cache_key] = translation
        return False, translation


def translate_subs(translator, language, dest_lang_1, dest_lang_2, WAITING_NEW_FILE=5):
    """
    Translate subtitle files from source language to destination languages.
    """
    sub_files = []
    sub_dest1, sub_dest2, sub_src, sub_pin, sub_all = "", "", "", "", ""

    if (
        language not in languageEnglish2Code
        or dest_lang_1 not in languageEnglish2Code
        or dest_lang_2 not in languageEnglish2Code
    ):
        print("Cannot find language name(s)", flush=True)
        exit(2)

    srclang = languageEnglish2Code[language]
    destlang1 = languageEnglish2Code[dest_lang_1]
    destlang2 = languageEnglish2Code[dest_lang_2]

    patterns = f"{SUBTITLE_DIR}/*.{srclang}.srt"
    for file in glob.glob(patterns):
        sub_src = file
        path, filename = os.path.split(sub_src)
        outpath = path

        base_name = filename.split(f".{srclang}.srt")[0]
        sub_dest1 = os.path.join(outpath, base_name + f".{destlang1}.srt")
        sub_dest2 = os.path.join(outpath, base_name + f".{destlang2}.srt")
        sub_pin = (
            os.path.join(outpath, base_name + ".py.srt") if srclang == "zh" else ""
        )
        sub_all = os.path.join(outpath, base_name + ".srt")

        if not (
            os.path.exists(sub_dest1)
            and os.path.exists(sub_dest2)
            and (not sub_pin or os.path.exists(sub_pin))
        ):
            sub_files.append(sub_src)
            break

    if not sub_files:
        time.sleep(WAITING_NEW_FILE)
        return

    NO_SUBTILE_TEXT = "^[0-9\n\r]"
    translation_cache = load_translation_cache()

    print(f"Start translating {sub_src}...", flush=True)
    with open(sub_src, "r", encoding="utf-8") as file_src:
        text_src = file_src.readlines()
        file_src.close()

        text_all = text_src.copy()
        text_pin = text_src.copy() if srclang == "zh" else []
        text_dest1 = text_src.copy()
        text_dest2 = text_src.copy()

        SLEEP_ONE = 1
        SLEEP_BATCH = 60

        index_translate = []
        text_translate = []

        for i, line in enumerate(text_src):
            if not re.match(NO_SUBTILE_TEXT, line):
                index_translate.append(i)
                text_translate.append(line.strip())

        NORMAL_MAX_TRANS = 100
        TEXT_ITEMS = len(text_translate)
        batches = round((TEXT_ITEMS / NORMAL_MAX_TRANS * 1.0) + 0.5)

        for b in range(batches):
            text_range = text_translate[
                b * NORMAL_MAX_TRANS : (b + 1) * NORMAL_MAX_TRANS
            ]
            combined_text = SEPARATOR.join(text_range)
            error_count = 0
            sleep = SLEEP_BATCH
            sleep_one = SLEEP_ONE

            while error_count < 5:
                try:
                    # use_cache, translation_dest1 = translate_offline_with_cache(
                    #     combined_text, srclang, destlang1, translation_cache
                    # )
                    use_cache, translation_dest1 = translate_with_cache(
                        combined_text, translator, srclang, destlang1, translation_cache
                    )
                    expanded_dest1 = translation_dest1.split(SEPARATOR)

                    if not use_cache:
                        if sleep_one > 5:
                            print(f"\tSleeping {sleep_one}s", flush=True, end="... ")
                        else:
                            print(f"", flush=True, end=".")

                        time.sleep(sleep_one)

                    # use_cache, translation_dest2 = translate_offline_with_cache(
                    #     combined_text, srclang, destlang2, translation_cache
                    # )
                    use_cache, translation_dest2 = translate_with_cache(
                        combined_text, translator, srclang, destlang2, translation_cache
                    )
                    expanded_dest2 = translation_dest2.split(SEPARATOR)

                    if srclang == "zh":
                        pin = pinyin_generator.pinyin(combined_text)
                        expanded_pin = pin.split(SEPARATOR)

                    break
                except Exception as ex:
                    print(ex, flush=True)
                    error_count += 1
                    print(f"\tSleeping {sleep}s", flush=True, end="... ")
                    time.sleep(sleep)
                    sleep = sleep * 1.5
                    sleep_one = sleep * 1.5

            count = 0
            for x in range(min(NORMAL_MAX_TRANS, TEXT_ITEMS - b * NORMAL_MAX_TRANS)):
                y = index_translate[b * NORMAL_MAX_TRANS + x]
                text_dest1[y] = expanded_dest1[count] + "\n"
                text_dest2[y] = expanded_dest2[count] + "\n"
                if srclang == "zh":
                    text_pin[y] = expanded_pin[count].strip() + "\n"
                    text_all[y] = text_src[y] + text_pin[y] + text_dest1[y]
                else:
                    text_all[y] = text_src[y] + text_dest1[y]
                count += 1

        with open(sub_dest1, "w", encoding="utf-8") as file:
            file.write("".join(text_dest1))
        with open(sub_dest2, "w", encoding="utf-8") as file:
            file.write("".join(text_dest2))
        if srclang == "zh":
            with open(sub_pin, "w", encoding="utf-8") as file:
                file.write("".join(text_pin))
        with open(sub_all, "w", encoding="utf-8") as file:
            file.write("".join(text_all))

        folder, file_name = os.path.split(sub_src)
        base_name = file_name[: file_name.find(".zh.srt")]
        moved_files = glob.glob(f"{SUBTITLE_DIR}/{base_name}*.*")

        # for file in moved_files:
        #     folder, file_name = os.path.split(file)
        #     shutil.move(file, os.path.join(DONE_SUBS_DIR, file_name))

    save_translation_cache(translation_cache)

    print(f"\n\tCombined file written {sub_all}", flush=True)
    # print(f"Waiting for new subtitle files in {SUBTITLE_DIR}...", flush=True)
    if not sub_files:
        for file in glob.glob(f"{SUBTITLE_DIR}*.{srclang}.srt"):
            sub_files.append(file)
        sub_files.sort(reverse=True)
        if not sub_files:
            return


def process_urls(file_path):
    """
    Process URLs from a file and download the corresponding media.
    """
    with open(file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()

    if lines[0].startswith("#"):
        urls = lines[1:]
    else:
        urls = lines

    remaining_urls = []

    for line in urls:
        url = line.strip()
        if not url:
            continue

        filename = None
        if "\t" in line:
            parts = line.split("\t")
            url = parts[0].strip()
            filename = parts[1].strip()

        print(f"Downloading {url}...", flush=True)

        try:
            if "youtube.com" in url or "youtu.be" in url:
                success = download_youtube_video(url)
            else:
                if not filename:
                    filename = os.path.basename(url)
                filename = clean_filename(filename)
                download_file(url, filename, MEDIA_DIR)
                success = True

            if not success:
                remaining_urls.append(line)
        except Exception as e:
            print(f"Failed to download {url}: {e}", flush=True)
            remaining_urls.append(line)

    with open(file_path, "w", encoding="utf-8") as file:
        if lines[0].startswith("#"):
            file.write(lines[0])
        for url in remaining_urls:
            file.write(url + "\n")


def check_for_subtitles(subtitle_dir):
    """
    Check if there are subtitles in the directory.
    """
    patterns = f"{subtitle_dir}/*.zh.srt"
    return bool(glob.glob(patterns))


def has_valid_extension(filename):
    """
    Check if a filename has a valid media extension.
    """

    file_extension = os.path.splitext(filename)[1].lower()
    return file_extension in MEDIA_EXTENSIONS


def transcribe_media(WAITING_NEW_FILE=5):
    """
    Transcribe media files to text and generate subtitles.
    """
    media_files = []

    process_urls(f"{MEDIA_DIR}/urls.txt")

    # if LANGUAGE == "zh":
    # converter = OpenCC("t2s")

    matching_files = []

    # Iterate over the set of extensions
    for ext in MEDIA_EXTENSIONS:
        # Use glob to find all files with the current extension
        files = glob.glob(os.path.join(MEDIA_DIR, f"*{ext}"))
        # Extend the matching files list with the files found
        matching_files.extend(files)

    for media_file in matching_files:
        if not pathvalidate.is_valid_filepath(media_file):
            new_media_file = pathvalidate.sanitize_filepath(media_file)
            new_media_file = new_media_file.replace(" ", "_")
            try:
                shutil.move(media_file, new_media_file)
                media_file = new_media_file
            except Exception as ex:
                print(ex, flush=True)

        media_files.append(media_file)

    # if not media_files:
    #     time.sleep(WAITING_NEW_FILE)
    #     return

    while media_files:
            
        media_file = media_files.pop()

        print(f"Start processing {no_current(media_file)} ({len(media_files)} files left)", flush=True)

        outpath = SUBTITLE_DIR
        json_meta = get_media_metadata(media_file)
        media_length = determine_media_length(json_meta)
        media_type = get_media_type(media_file)

        print(f"\t*** Media length {format_duration(media_length)}", flush=True)

        path, filename = os.path.split(media_file)
        base_name, extension = os.path.splitext(filename)
        base_path = os.path.join(outpath, base_name)
        new_media_file = os.path.join(outpath, base_name) + extension

        wav_file = base_path + ".wav"
        mp4_file = base_path + ".mp4"
        mp3_file = base_path + ".mp3"
        sub_zho = base_path + ".zh.srt"
        txt_sub = base_path + ".txt"

        if not convert_media(media_file, wav_file):
            print(f"\tError during conversion: {no_current(media_file)}")
        else:
            print(
                f"\tConversion successful: {no_current(media_file)} -> {no_current(wav_file)}"
            )

        if media_type == 2:  # Media file, then creates an audio fle
            if not convert_media(media_file, mp3_file):
                print(f"\tError during conversion: {no_current(media_file)}")
            else:
                print(
                    f"\tConversion successful: {no_current(media_file)} -> {no_current(mp3_file)}"
                )
        elif media_type == 1:  # Audio file, then creates an video fle
            if not make_black_video_file(media_file, mp4_file, media_length):
                print(f"\tError during conversion: {no_current(media_file)}")
            else:
                print(
                    f"\tConversion successful: {no_current(media_file)} -> {no_current(mp4_file)}"
                )

        # print(f"\tAudio file exported {no_current(audio_file)}", flush=True)

        r = sr.Recognizer()

        with sr.AudioFile(wav_file) as source:
            audio_text = r.record(source)

        print(f"\tStarting transcription {no_current(wav_file)}...", flush=True)

        start = time.time()

        result = r.recognize_whisper(
            audio_text, language=LANGUAGE, show_dict=True, word_timestamps=True
        )
        os.remove(wav_file)
        end = time.time()

        print(
            f"\t*** Time elapsed {format_duration(end - start)} - Media length {format_duration(media_length)} - relative speed {media_length/(end - start):.1f}x",
            flush=True,
        )

        subs = pysrt.SubRipFile()
        sub_idx = 1
        item_count = len(result["segments"])
        lines = []

        for i in range(item_count):
            start_time = result["segments"][i]["start"]
            end_time = result["segments"][i]["end"]
            text = result["segments"][i]["text"]

            if languageEnglish2Code[LANGUAGE] == "zh":
                text = chinese_converter.to_simplified(text)
                # text = text.replace("v̌", "ǚ")

            sub = pysrt.SubRipItem(
                index=sub_idx,
                start=pysrt.SubRipTime(seconds=start_time),
                end=pysrt.SubRipTime(seconds=end_time),
                text=text,
            )

            if text.strip():
                lines.append(text)

            subs.append(sub)
            sub_idx += 1

        if not subs:
            print(f"Subtitle empty {sub_zho}", flush=True)
        else:
            subs.save(sub_zho)

            with open(txt_sub, "w", encoding="utf-8") as file:
                file.write("\n".join(lines))

            print(f"\tSubtitle written {no_current(sub_zho)}", flush=True)
            print(f"Waiting for new media files in {MEDIA_DIR}...", flush=True)

        shutil.move(media_file, new_media_file)


def main():
    """
    Main entry point for the script.
    """
    global MEDIA_DIR, SUBTITLE_DIR, TRANSLATOR_SERVICE, LANGUAGE, DEST_LANGUAGE_1, DEST_LANGUAGE_2

    initial_checks()

    LOOP_FOREVER = False

    if LOOP_FOREVER:
        print("Waiting for new media files...", flush=True)
        while True:
            process_urls(URL_FILE)
            transcribe_media(1)
            translate_subs(
                TRANSLATOR_SERVICE, LANGUAGE, DEST_LANGUAGE_1, DEST_LANGUAGE_2, 0
            )
    else:
        print("Waiting for new media files...", flush=True)
        transcribe_media(1)
        translate_subs(
            TRANSLATOR_SERVICE, LANGUAGE, DEST_LANGUAGE_1, DEST_LANGUAGE_2, 0
        )


if __name__ == "__main__":
    main()
