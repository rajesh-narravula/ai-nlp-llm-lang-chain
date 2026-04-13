import whisper

import os
from tabulate import tabulate

audio_files_folder = r'C:\Users\rajesh.narravula\OneDrive - Accenture\Documents\python\speech_recognition\Recordings'


def transcribe_audio_whisper(file_path):
    translated_texts = []
    for file_name in os.listdir(file_path):
        if file_name.endswith('.wav'):
            full_path = os.path.join(file_path, file_name)
            model = whisper.load_model("base")
            result = model.transcribe(full_path)
            translated_text = {"file_name": file_name, "transcribed_text": result['text']}
            translated_texts.append(translated_text)
    return translated_texts

        
transcribed_text = transcribe_audio_whisper (audio_files_folder)
print(tabulate(transcribed_text, headers="keys", tablefmt="grid"))

