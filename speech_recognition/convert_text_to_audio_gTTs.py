
import os
from gtts import gTTS


ground_truth = """The stale smell of old beer lingers. It takes heat to bring out the odor. A cold dip restores health and zest. A salt pickle tastes fine with ham. Tacos al pastor are my favorite. A zestful food is the hot cross bun."""

tts = gTTS(ground_truth, lang='en')

tts.save('output_audio.mp3')

os.system('start output_audio.mp3')
