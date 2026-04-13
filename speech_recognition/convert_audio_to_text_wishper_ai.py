import numpy as np
import matplotlib.pyplot as plt

import librosa
import librosa.display
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr

from jiwer import wer, cer

import whisper

import csv
import tempfile
import wave

from gtts import gTTS

audio_file = 'harvard.wav'

recognizer = sr.Recognizer()

def transcribe_audio(file_path):
    with sr.AudioFile(file_path) as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Could not understand audio"
        except sr.RequestError as e:
            return f"Could not request results; {e}"
        
        
transcribed_text = transcribe_audio(audio_file)
print(f"Transcribed Text: {transcribed_text}")

ground_truth = """The stale smell of old beer lingers. It takes heat to bring out the odor. A cold dip restores health and zest. A salt pickle tastes fine with ham. Tacos al pastor are my favorite. A zestful food is the hot cross bun."""

wer_value = wer(ground_truth, transcribed_text)

cer_value = cer(ground_truth, transcribed_text)

print(f"Word Error Rate (WER): {wer_value:.4f}")
print(f"Character Error Rate (CER): {cer_value:.4f}")


audio_signal, sample_rate = librosa.load(audio_file, sr=None)


signal_filtered = librosa.effects.preemphasis(audio_signal, coef=0.97)
sf.write('filtered_audio.wav', signal_filtered, sample_rate)


transcribed_text_preemphasis = transcribe_audio('filtered_audio.wav')
print(f"Transcribed Text (Pre-emphasized): {transcribed_text_preemphasis}")

wer_value_preemphasis = wer(ground_truth, transcribed_text_preemphasis)

cer_value_preemphasis = cer(ground_truth, transcribed_text_preemphasis)

print(f"Word Error Rate for Pre-emphasized Audio (WER): {wer_value_preemphasis:.4f}")
print(f"Character Error Rate for Pre-emphasized Audio (CER): {cer_value_preemphasis  :.4f}")

# By using Whisper AI
model = whisper.load_model("base")
result = model.transcribe(audio_file)
print(f"Whisper Transcribed Text: {result['text']}")

wer_value_whisper = wer(ground_truth, result['text'])

cer_value_whisper = cer(ground_truth, result['text'])

print(f"Word Error Rate for Whisper (WER): {wer_value_whisper:.4f}")
print(f"Character Error Rate for Whisper (CER): {cer_value_whisper  :.4f}")

