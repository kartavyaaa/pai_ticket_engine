import tempfile
import os
import base64
from gtts import gTTS
import speech_recognition as sr
from pydub import AudioSegment

# -----------------------
# Speech-to-Text
# -----------------------
def transcribe_audio(audio_bytes: bytes, filename="audio.wav") -> str:
    rec = sr.Recognizer()

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
        f.write(audio_bytes)
        infile = f.name

    outfile = infile + "_converted.wav"

    try:
        audio = AudioSegment.from_file(infile)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(outfile, format="wav")

        with sr.AudioFile(outfile) as source:
            data = rec.record(source)

        text = rec.recognize_google(data)
        return text

    except Exception as e:
        return f"[Error transcribing: {e}]"

    finally:
        for fp in [infile, outfile]:
            try:
                os.remove(fp)
            except:
                pass


# -----------------------
# Text-to-Speech
# -----------------------
def text_to_speech(text: str) -> bytes:
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as f:
        mp3_path = f.name

    tts = gTTS(text)
    tts.save(mp3_path)

    with open(mp3_path, "rb") as f:
        data = f.read()

    os.remove(mp3_path)
    return data
