
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
