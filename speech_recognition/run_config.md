> python -m venv speech_env

> speech_env\Scripts\activate


> pip install librosa
> pip install SpeechRecognition
> pip install jiwer
> pip install matplotlib
> pip install gTTS

Install PyTorch:
o Go to the PyTorch website(https://pytorch.org/) and select the “Get Started” option.
o Under “Start locally”, configure the following:
▪ Stable version
▪ Your operating system (e.g., Windows, macOS)
▪ Package: pip
▪ Language: Python
▪ Compute platform: Select a CUDA version if you have a GPU or select
CPU.
o Copy the provided installation command and paste it into Anaconda Prompt,
then press Enter.

Install FFmpeg:
To install ffmpeg (FFmpeg is essential for Whisper to handle various audio formats)

Go to https://ffmpeg.org/download.html → Windows → gyan.dev or BtbN builds
Download the .zip (e.g., ffmpeg-release-essentials.zip)
Extract to C:\ffmpeg
Add C:\ffmpeg\bin to your System PATH:

Search "Environment Variables" → System Properties → Environment Variables
Under System variables, find Path → Edit → New → C:\ffmpeg\bin

Open a new terminal and run: ffmpeg -version

> pip install -U openai-whisper
> pip install sounddevice
> pip install tabulate

> pip install -U librosa SpeechRecognition jiwer matplotlib gTTS