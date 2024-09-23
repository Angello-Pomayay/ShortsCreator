import os
import random
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, CompositeAudioClip

# Folder paths
videos_folder = "../SourceVideos"
bg_music_folder = "../bg_music"

# --- old function ---
#    def select_random_videos(folder, count):
       # """Selects random videos from the given folder."""
       # videos = os.listdir(folder)
       # selected_videos = random.sample(videos, count)
       # return [os.path.join(folder, video) for video in selected_videos]

def select_random_videos(folder, count):
    """Selects random videos from the given folder that are at least 15 seconds long."""
    videos = os.listdir(folder)
    valid_videos = []

    while len(valid_videos) < count:
        # Select random videos from the folder
        selected_videos = random.sample(videos, count - len(valid_videos))

        for video in selected_videos:
            video_path = os.path.join(folder, video)
            try:
                # Check if the video duration is at least 14 seconds, 1 sec delay should be okay for the user
                with VideoFileClip(video_path) as clip:
                    if clip.duration >= 14:
                        valid_videos.append(video_path)

            except Exception as e:
                print(f"Error processing video {video}: {e}")

    return valid_videos

def apply_darkening_effect(video_clip, brightness=0.5):
    """Applies a darkening effect to the given video clip."""
    return video_clip.fx(vfx.colorx, brightness)

try:
    # Select 4 random videos from the folder
    selected_videos = select_random_videos(videos_folder, 4)

    # Load and concatenate the selected videos to create a 15-second background each
    background_clips = [VideoFileClip(video).subclip(0, 15) for video in selected_videos]
    background_clip = concatenate_videoclips(background_clips, method="compose")

    # Load personal audio
    personal_audio = AudioFileClip("../audio_temp/final_audio.wav")

    # Trim the background video to match the duration of personal_audio
    background_clip = background_clip.subclip(0, personal_audio.duration)

    # Set audio for the background video
    background_clip = background_clip.set_audio(personal_audio)

    # Apply darkening effect to the background video
    background_clip_dark = apply_darkening_effect(background_clip, brightness=0.5)

    # Select a random music track
    selected_music = random.choice(os.listdir(bg_music_folder))
    music_path = os.path.join(bg_music_folder, selected_music)

    # Load the music track
    music_clip = AudioFileClip(music_path)

    # Adjust the volume of the music track
    music_clip = music_clip.volumex(0.2)

    # Make the music clip the same duration as the background video
    music_clip = music_clip.set_duration(background_clip_dark.duration)

    # Combine background video with music
    final_audio = CompositeAudioClip([background_clip_dark.audio, music_clip])

    # Set the composite audio to the background video
    final_clip = background_clip_dark.set_audio(final_audio)

    # Export the final video with both audio tracks
    final_clip.write_videofile("OutputVideos/bg_video.mp4", codec='libx264', audio_codec='aac', fps=24, preset="ultrafast")

except Exception as e:
    print("An error occurred:", e)
