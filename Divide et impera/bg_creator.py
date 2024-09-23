import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, CompositeAudioClip

# Folder path for source videos
videos_folder = "SourceVideos"
bg_music_folder = "bg_music"

# Select 4 random videos from the folder
selected_videos = random.sample(range(314), 4)

# Load and concatenate the selected videos to create a 15-second background each
background_clips = [VideoFileClip(os.path.join(videos_folder, f"{video}.mp4")).subclip(0, 15) for video in selected_videos]
background_clip = concatenate_videoclips(background_clips, method="compose")

# Load personal audio
personal_audio = AudioFileClip("../audio_temp/final_audio.wav")

# Set audio for the background video
background_clip = background_clip.set_audio(personal_audio)

# Apply darkening effect to the background video
background_clip_dark = background_clip.fx(vfx.colorx, 0.5)  # Adjust brightness here (0.5 makes it darker)

# Select a random music track
selected_music = random.choice(os.listdir(bg_music_folder))
music_path = os.path.join(bg_music_folder, selected_music)

# Load the music track
music_clip = AudioFileClip(music_path)

# Adjust the volume of the music track to 50%
music_clip = music_clip.volumex(0.2)

# Make the music clip the same duration as the background video (60 seconds)
music_clip = music_clip.set_duration(background_clip_dark.duration)

# Combine background video with music
final_audio = CompositeAudioClip([background_clip_dark.audio, music_clip])

# Set the composite audio to the background video
final_clip = background_clip_dark.set_audio(final_audio)

# Export the final video with both audio tracks as an MP4 file
final_clip.write_videofile("OutputVideos/bg_video.mp4", codec='libx264', audio_codec='aac', fps=24, preset="ultrafast")
