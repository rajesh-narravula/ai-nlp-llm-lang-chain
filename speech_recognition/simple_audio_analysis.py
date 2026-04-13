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


audio_signal, sample_rate = librosa.load('music-wav.wav', sr=None)

print(sample_rate)


plt.figure(figsize=(14, 5))
librosa.display.waveshow(audio_signal, sr=sample_rate)
plt.title('Audio Signal')
plt.xlabel('Time (s)')
plt.ylabel('Amplitude')
plt.show()

sd.play(audio_signal, sample_rate)
sd.wait()