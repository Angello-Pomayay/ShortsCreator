# Angello Fernando Pomayay Gabonal
#
# Applicazione in python per la creazione semi-automatizzata di media per le piattaforme di condivisione video
from elevenlabs import play, stream, save
from elevenlabs.client import ElevenLabs
from audiostretchy.stretch import stretch_audio
from typing import Sequence, Optional
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, concatenate_videoclips, AudioFileClip, vfx, CompositeAudioClip, TextClip, CompositeVideoClip
from dotenv import load_dotenv

import pvleopard
import fitz  # PyMuPDF
import os
import random
import sys
import pysrt

load_dotenv()

client = ElevenLabs(
  api_key=os.getenv('ELEVENLABS_API_KEY')
)
leopard = pvleopard.create(access_key=os.getenv('PICOVOICE_ACCESSKEY'))

name_index=0

def adam_voice(text): # CREATION OF AUDIO WITH THE API
    single_line_text = ' '.join(text.splitlines())
    audio = client.generate(
        text=single_line_text,
        voice="Adam",
        model="eleven_multilingual_v2"
    )

    save(audio, "audio_temp/adam_voice.wav")

def audio_stretcher():
    # Set input and output file names for initial and final audio
    input_file = "audio_temp/adam_voice.wav"  # Replace with your actual input file
    stretched_output_file = "audio_temp/output_stretched_audio.wav"
    final_output_file = "audio_temp/final_audio.wav"

    # Load the initial audio file
    audio = AudioSegment.from_file(input_file)

    # Set the desired duration (60 seconds in this case)
    desired_duration = 59800  # in milliseconds

    # Check if the duration is less than or equal to 60 seconds
    if len(audio) <= desired_duration:
        print("Audio is already 60 seconds or less. No stretching needed.")
        audio.export(final_output_file, format="wav")
        print(f"Audio saved as {final_output_file}")
    else:
        # Convert the input audio file to a supported format (e.g., WAV)
        audio.export("audio_temp/temp_input.wav", format="wav")
        input_file = "audio_temp/temp_input.wav"

        # Calculate the stretching ratio
        ratio = desired_duration / len(audio)

        try:
            # Perform audio stretching
            stretch_audio(input_file, stretched_output_file, ratio=ratio)
            print(f"Audio stretched successfully and saved to {stretched_output_file}")
        except Exception as e:
            print(f"Error during stretching: {e}")

    # Check if the stretched audio file exists before loading it
    if os.path.exists(stretched_output_file):
        # Load the stretched audio file
        audio = AudioSegment.from_file(stretched_output_file)

        # Cut the audio at the desired duration
        cut_audio = audio[:desired_duration]

        # Export the cut audio to a new file
        cut_audio.export(final_output_file, format="wav")
        print(f"Audio cut successfully at 60 seconds and saved to {final_output_file}")
    else:
        print("Stretched audio file not found. Cannot proceed with cutting.")

    # Clean up temporary files
    if os.path.exists("audio_temp/temp_input.wav"):
        os.remove("audio_temp/temp_input.wav")

    if os.path.exists("audio_temp/output_stretched_audio.wav"):
        os.remove("audio_temp/output_stretched_audio.wav")

def srt_creator():
    def get_audio_duration(audio_file: str) -> float:
        audio = AudioSegment.from_file(audio_file)
        return len(audio) / 1000  # Convert milliseconds to seconds

    def second_to_timecode(x: float) -> str:
        hour, x = divmod(x, 3600)
        minute, x = divmod(x, 60)
        second, x = divmod(x, 1)
        millisecond = int(x * 1000.)
        return '%.2d:%.2d:%.2d,%.3d' % (hour, minute, second, millisecond)

    def to_srt(
            words: Sequence[pvleopard.Leopard.Word],
            audio_file: str,
            endpoint_sec: float = 1.,
            length_limit: Optional[int] = 1) -> str:
        audio_duration = get_audio_duration(audio_file)

        def _helper(end: int) -> None:
            lines.append("%d" % section)
            if end == len(words) - 1:
                # If it's the last word, set the end time to the duration of the audio file
                lines.append(
                    "%s --> %s" %
                    (
                        second_to_timecode(words[start].start_sec),
                        second_to_timecode(audio_duration)
                    )
                )
            else:
                lines.append(
                    "%s --> %s" %
                    (
                        second_to_timecode(words[start].start_sec),
                        second_to_timecode(words[end].end_sec)
                    )
                )
            lines.append(' '.join(x.word for x in words[start:(end + 1)]))
            lines.append('')

        lines = list()
        section = 0
        start = 0
        for k in range(1, len(words)):
            if ((words[k].start_sec - words[k - 1].end_sec) >= endpoint_sec) or \
                    (length_limit is not None and (k - start) >= length_limit):
                _helper(k - 1)
                start = k
                section += 1
        _helper(len(words) - 1)

        return '\n'.join(lines)

    transcript, words = leopard.process_file("audio_temp/final_audio.wav")

    with open('audio_temp/sub.srt', 'w') as f:
        f.write(to_srt(words, "audio_temp/final_audio.wav"))  # Pass the audio file path

def srt_corrector():
    def modify_srt_file(input_file, output_file):
        with open(input_file, 'r') as f:
            lines = f.readlines()

        modified_lines = []
        for i in range(0, len(lines), 4):
            seq_number = lines[i].strip()
            time_range = lines[i + 1].strip()
            caption = lines[i + 2].strip().upper()  # Convert caption to uppercase

            # Extract start and end times
            start_time, end_time = time_range.split(' --> ')

            # Extract next start time if available
            if i + 5 < len(lines):
                next_start_time = lines[i + 5].split(' --> ')[0].strip()
            else:
                # Handle the last caption
                next_start_time = end_time  # Keep the end time of the last caption as the next start time

            # Append modified lines
            modified_lines.extend([seq_number, '\n', f"{start_time} --> {next_start_time}", '\n', caption, '\n', '\n'])

        with open(output_file, 'w') as f:
            f.writelines(modified_lines)

    modify_srt_file("audio_temp/sub.srt", "audio_temp/sub_final.srt")

def bg_creator():
    videos_folder = "SourceVideos"
    bg_music_folder = "bg_music"

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
        personal_audio = AudioFileClip("audio_temp/final_audio.wav")

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
        final_clip.write_videofile("OutputVideos/bg_video.mp4", codec='libx264', audio_codec='aac', fps=24,
                                   preset="ultrafast")

    except Exception as e:
        print("An error occurred:", e)

def final_video_assembler():
    global name_index
    # Place files in this path or modify the paths to point to where the files are
    srtfilename = "audio_temp/sub_final.srt"
    mp4filename = "OutputVideos/bg_video.mp4"

    def time_to_seconds(time_obj):
        return time_obj.hours * 3600 + time_obj.minutes * 60 + time_obj.seconds + time_obj.milliseconds / 1000

    def create_subtitle_clips(subtitles, videosize, fontsize=60, font='fonts/Montserrat-ExtraBold.ttf', color='white',
                              outline_color='black', outline_width=-5, letter_spacing=0, debug=False):
        subtitle_clips = []

        for subtitle in subtitles:
            start_time = time_to_seconds(subtitle.start)
            end_time = time_to_seconds(subtitle.end)
            duration = end_time - start_time

            video_width, video_height = videosize

            text_clip = TextClip(subtitle.text, fontsize=fontsize, font=font, color=color, bg_color='none',
                                 stroke_color='none', stroke_width=0,
                                 size=(video_width * 9 / 10, None), method='caption', kerning=-3).set_start(
                start_time).set_duration(
                duration)
            subtitle_x_position = 'center'
            subtitle_y_position = 'center'

            text_position = (subtitle_x_position, subtitle_y_position)
            subtitle_clips.append(text_clip.set_position(text_position))

        return subtitle_clips

    video = VideoFileClip(mp4filename)
    subtitles = pysrt.open(srtfilename)

    begin, end = mp4filename.split(".mp4")
    output_video_file = "OutputVideos/"+f"{name_index}" + ".mp4"

    print("Output file name: ", output_video_file)

    # Create subtitle clips
    subtitle_clips = create_subtitle_clips(subtitles, video.size)

    # Add subtitles to the video
    final_video = CompositeVideoClip([video] + subtitle_clips)

    # Write output video file
    final_video.write_videofile(output_video_file)

    name_index = name_index + 1

def process_text(text): # This is the principal function that will call all the other functions -----------------------
    print(text+"\n------------------------------------------------\n\n")
    adam_voice(text)
    audio_stretcher()
    srt_creator()
    srt_corrector()
    bg_creator()
    final_video_assembler()

    pass

def read_pdf_until_special_combination(pdf_path, special_combination, start_index=0, num_parts=1):
    doc = fitz.open(pdf_path)
    remaining_text = ""

    parts_processed = 0  # Counter for the number of parts processed

    for page_num in range(doc.page_count):
        page = doc.load_page(page_num)
        text = remaining_text + page.get_text()

        while True:
            # Find the index of the special combination in the text
            special_comb_index = text.find(special_combination)

            if special_comb_index == -1:
                break  # Special combination not found on this page

            # Extract text before the special combination
            truncated_text = text[:special_comb_index].strip()

            # Check if this part of text should be processed
            if parts_processed >= start_index and parts_processed < start_index + num_parts:
                # Process the text if within the specified range
                process_text(truncated_text)

            parts_processed += 1  # Increment the parts counter

            # Update text to continue searching after the special combination
            text = text[special_comb_index + len(special_combination):].strip()

            # Exit loop if reached the specified number of parts
            if parts_processed >= start_index + num_parts:
                return

        # Store the remaining text for the next iteration
        remaining_text = text

    # Print any remaining text after the last page
    if remaining_text and parts_processed >= start_index and parts_processed < start_index + num_parts:
        process_text(remaining_text)


pdf_path = 'PDF_folder/jokes.pdf'

special_combination = '****'

# Call the function to read PDF and process text from the specified part
start_index = 1  # Index of the part of text to start from
num_parts = 1    # Number of parts of text to process
read_pdf_until_special_combination(pdf_path, special_combination, start_index, num_parts)
