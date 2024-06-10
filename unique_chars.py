import re

chars = set()


def read_file_and_print_unique_non_alphanumeric(filename):
    global chars
    try:
        with open(filename, "r", encoding="utf-8") as file:
            text = file.read()

            # Find all unique characters that are not alphanumeric
            unique_non_alphanumeric_chars = set(re.findall(r"[^0-9a-zA-Z]", text))

            print("Unique non-alphanumeric characters:")
            for char in sorted(unique_non_alphanumeric_chars):
                chars.add(char)
                print(char)

    except FileNotFoundError:
        print(f"File {filename} not found.")
    except Exception as e:
        print(f"An error occurred: {e}")


import pinyin_jyutping

p = pinyin_jyutping.PinyinJyutping()
pinyin_with_tone_marks = p.pinyin("女生。你好，世界")
print("Pinyin with tone marks:", pinyin_with_tone_marks)

import pinyin

print(pinyin.get("女生。你好，世界", delimiter=" "))

# Replace 'your_file.txt' with the path to your text file
read_file_and_print_unique_non_alphanumeric(
    r"C:\Users\it.fsoft\OneDrive - FPT Corporation\Personal\Playground\transcribe\downloads\subs\One Call Awaw - 05 在親密關係中不夠自信嗎？Not Confident In An Intimate Relationship.py.srt"
)
