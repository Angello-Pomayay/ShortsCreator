from TTS.api import TTS

text = """Three spies are captured by a terrorist group: French, German and an
Italian.
 
The captors first take the French spy for interrogation. They tie his hands
behind a chair and torture him for two hours before he spills the beans. The
captors throw him back into the cell and drag the German in for their
interrogation. Like before, they tie his hands behind the chair and begin
torturing him. The German resists for four hours before giving in. The
captors throw him back into the cell and then drag the Italian. They again
tie his hands behind the chair and begin torturing him. Four hours pass by,
then eight, then sixteen and even twenty four hours later, the interrogators
had not gotten a word out of the Italian. Frustrated, they throw him back
into the cell.
 
Impressed by the Italian’s resistance, the other two spies ask him, “How did
you manage to keep quiet for so long?” The Italian responds, “Oh, I wanted
to talk. But I just could not move my hands.”"""

single_line_text = ' '.join(text.splitlines())
print(single_line_text)

tts = TTS(model_name="tts_models/en/ljspeech/tacotron2-DDC")
tts.tts_to_file(text= single_line_text, lang="en", filename="audio_temp/output.wav")