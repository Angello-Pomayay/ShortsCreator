from pydub import AudioSegment
from audiostretchy.stretch import stretch_audio
import os

# Set input and output file names for initial and final audio
input_file = "../audio_temp/adam_voice.wav"
stretched_output_file = "audio_temp/output_stretched_audio.wav"
final_output_file = "../audio_temp/final_audio.wav"

# Load the initial audio file
audio = AudioSegment.from_file(input_file)

# Set the desired duration in milliseconds
desired_duration = 59800

# Check if the duration is less than or equal to desired_duration (59.8 = ~60 seconds)
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
