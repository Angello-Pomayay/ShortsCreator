# Place files in this path or modify the paths to point to where the files are
srtfilename = "audio_temp/sub_final.srt"
mp4filename = "OutputVideos/bg_video.mp4"

import sys
import pysrt
from moviepy.editor import VideoFileClip, TextClip, CompositeVideoClip


def time_to_seconds(time_obj):
    return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000


def create_subtitle_clips(subtitles, videosize, fontsize=60, font='fonts/Montserrat-ExtraBold.ttf', color='white', outline_color='black', outline_width=-5, letter_spacing=0, debug=False):
    subtitle_clips = []

    for subtitle in subtitles:
        start_time = time_to_seconds(subtitle.start)
        end_time = time_to_seconds(subtitle.end)
        duration = end_time - start_time

        video_width, video_height = videosize

        text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color, bg_color='none',
                             stroke_color='none', stroke_width=0,
                             size=(video_width * 9/10, None), method='caption', kerning=-3).set_start(start_time).set_duration(
            duration)
        subtitle_x_position = 'center'
        subtitle_y_position = 'center'

        text_position = (subtitle_x_position, subtitle_y_position)
        subtitle_clips.append(text_clip.set_position(text_position))

    return subtitle_clips



video = VideoFileClip(mp4filename)
subtitles = pysrt.open(srtfilename)

begin,end= mp4filename.split(".mp4")
output_video_file = begin+'_subtitled'+".mp4"

print ("Output file name: ",output_video_file)

# Create subtitle clips
subtitle_clips = create_subtitle_clips(subtitles,video.size)

# Add subtitles to the video
final_video = CompositeVideoClip([video] + subtitle_clips)

# Write output video file
final_video.write_videofile(output_video_file)