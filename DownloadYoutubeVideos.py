""" Download all videos and their captions from a specified playlist
"""
import os
from pytube import YouTube, Playlist

INVALID_CHARS = set(r'<>:"/\|?*')

SAVE_PATH = r"./downloads" #to_do  

# link of the video to be downloaded  

# video_link = "https://www.youtube.com/watch?v=H0xNvQXI4Vw"
# list_link = "https://www.youtube.com/playlist?list=PL2vUQA5Qbw-G5GReNyWAK8XBrmAhxeaka" # Khóa 2 Tứ niệm xứ
#list_link = "https://www.youtube.com/playlist?list=PL2vUQA5Qbw-G5GReNyWAK8XBrmAhxeaka" # Khóa 3 HỌC và THỰC HÀNH Phật Pháp trong sinh hoạt

#list_link = "https://www.youtube.com/playlist?list=PLSIJismKOisEd-tT5MYM1391R9nRRI3U5" # Đi về nơi có gió
#list_link = "https://www.youtube.com/watch?v=hYDtKH3awpU&list=PL75pV8lKD9f7w-eHjuFPomTJLA9Kf1CrK" # Xiao Zhu Peiqi
list_link = "https://www.youtube.com/playlist?list=PL0eGJygpmOH6SOH7RK3BexJFWkHTxbmZi"
 
try:  

    playlist = Playlist(list_link)  

except:  

    print("Connection Error") #to handle exception
    exit(1)

print(playlist.video_urls)

videos = list(playlist.video_urls)

first_video = 0 # Fisrt one to download
last_video = -1 # Last one to download
track_to_download = 'a.vi' # Select Vietnamese audio track
create_srt_notime = True
download_videos = True
add_num_to_filename = True

for num, link in enumerate(videos[first_video:]):
    num_str = f'{first_video+num+1:02d}-'
    try:  

        yt = YouTube(link)  

    except:  

        print("Connection Error") #to handle exception
        continue

    print('%2i - %s - %s' % (num, link, yt.title))

    # Select video/audio to download
    audio = yt.streams.filter(type='video', mime_type='video/mp4', res="720p", progressive=False)[0]

    title = yt.title

    # Clean up title to use as filenames
    if add_num_to_filename:
        filetitle = num_str + ''.join([i for i in title if i not in INVALID_CHARS])
    else:
        filetitle = ''.join([i for i in title if i not in INVALID_CHARS])

    if filetitle[-1] == '.':
        filetitle = filetitle[:-1]

    print(filetitle)

    srt_filename = f'{filetitle}.srt'
    srt_notime_filename = f'{filetitle}_notime.srt'
    mp4_filename = f'{filetitle}.mp4'

    # Select Vietnamese auto-generated caption
    if track_to_download in yt.captions:
        caption = yt.captions[track_to_download]

        caption_lines = caption.generate_srt_captions().splitlines()
        # Get caption lines and keep only text (not time and count)    
        lines = caption_lines

        with open(os.path.join(SAVE_PATH, srt_filename), encoding='utf-8', mode='w') as f:
            for line in lines:
                f.write(f"{line}\n")

        lines_notime = caption_lines[2::4]

        with open(os.path.join(SAVE_PATH, srt_notime_filename), encoding='utf-8', mode='w') as f:
            for line in lines_notime:
                f.write(f"{line}\n")

    try:  
        print('Downloading the video...')

        if download_videos:
            audio.download(SAVE_PATH, filename=mp4_filename)
        
        print('done')

    except:  

        print("Some Error!")  

print('Task Completed!')  
 