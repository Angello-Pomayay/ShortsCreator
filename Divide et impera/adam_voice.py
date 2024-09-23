from elevenlabs import play, stream, save
from elevenlabs.client import ElevenLabs
from pydub import AudioSegment
from dotenv import load_dotenv
import os

load_dotenv()

client = ElevenLabs(
  api_key=os.getenv('ELEVENLABS_API_KEY')
)
text = """The maid requested a raise and the lady of the house was unhappy about it.
She asked, “Now, Jessica, why do you think you deserve a raise?”
Jessica: “There are three reasons why I requested the raise. First, I iron
better than you do.”
Lady of the house: “Who said that?”
Jessica: “Why, your husband.”
Lady of the house: “Oh, OK. What is the second reason?”
Jessica: “Second, I cook better than you.”
Lady of the house: “Who said that?”
Jessica: “Your husband.”
Lady of the house: “And, what is the third reason?”
Jessica: “Third, I am better in bed than you.”
Lady of the house, angrily: “Did my husband say that?”
Jessica: “No, the pool boy did.”
Jessica got the raise she was looking for"""

single_line_text = ' '.join(text.splitlines())
# Genera l'audio
audio = client.generate(
  text=single_line_text,
  voice="Adam",
  model="eleven_multilingual_v2"
)

save(audio, "../audio_temp/adam_voice.wav")