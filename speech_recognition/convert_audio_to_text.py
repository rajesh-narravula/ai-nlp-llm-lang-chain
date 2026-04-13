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

ground_truth = """The stale smell of old beer lingers.
It takes heat to bring out the odor.
A cold dip restores health and zest.
A salt pickle tastes fine with ham.
Tacos al pastor are my favorite.
A zestful food is the hot cross bun."""

wer_value = wer(ground_truth, transcribed_text)

cer_value = cer(ground_truth, transcribed_text)

print(f"Word Error Rate (WER): {wer_value:.4f}")
print(f"Character Error Rate (CER): {cer_value:.4f}")

# Spectrogram

audio_signal, sample_rate = librosa.load(audio_file, sr=None)
s = librosa.stft(audio_signal)
s_db = librosa.amplitude_to_db(np.abs(s), ref=np.max)
plt.figure(figsize=(14, 5))
librosa.display.specshow(data=s_db, sr=sample_rate, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Spectrogram')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.show()

singanl_filtered = librosa.effects.preemphasis(audio_signal, coef=0.97)
sf.write('filtered_audio.wav', singanl_filtered, sample_rate)

sb = librosa.stft(singanl_filtered)
s_dbd = librosa.amplitude_to_db(np.abs(sb), ref=np.max)
plt.figure(figsize=(14, 5))
librosa.display.specshow(data=s_dbd, sr=sample_rate, x_axis='time', y_axis='log')
plt.colorbar(format='%+2.0f dB')
plt.title('Filtered Spectrogram')
plt.xlabel('Time (s)')
plt.ylabel('Frequency (Hz)')
plt.show()


transcribed_text_preemphasis = transcribe_audio('filtered_audio.wav')
print(f"Transcribed Text (Pre-emphasized): {transcribed_text_preemphasis}")

wer_value_preemphasis = wer(ground_truth, transcribed_text_preemphasis)

cer_value_preemphasis = cer(ground_truth, transcribed_text_preemphasis)

print(f"Word Error Rate for Pre-emphasized Audio (WER): {wer_value_preemphasis:.4f}")
print(f"Character Error Rate for Pre-emphasized Audio (CER): {cer_value_preemphasis  :.4f}")

