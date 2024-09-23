from typing import Sequence, Optional
from pydub import AudioSegment
from dotenv import load_dotenv

import pvleopard
import os

leopard = pvleopard.create(access_key=os.getenv('PICOVOICE_ACCESSKEY'))


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

with open('../audio_temp/sub.srt', 'w') as f:
    f.write(to_srt(words, "../audio_temp/final_audio.wav"))  # Pass the audio file path
