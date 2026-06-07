import os
from datetime import datetime
from pathlib import Path
from gtts import gTTS

BASE_DIR = Path(os.path.dirname(os.path.abspath(__file__))).parent
VOICE_DIR = BASE_DIR / 'voice'
VOICE_DIR.mkdir(parents=True, exist_ok=True)

SUPPORTED_LANGUAGE_CODES = {'ta', 'te', 'hi', 'kn', 'ml', 'en'}


def generate_voice(text, language_code='en'):
    if language_code not in SUPPORTED_LANGUAGE_CODES:
        language_code = 'en'

    timestamp = datetime.utcnow().strftime('%Y%m%d%H%M%S')
    filename = f'voice_{language_code}_{timestamp}.mp3'
    output_path = VOICE_DIR / filename

    tts = gTTS(text=text, lang=language_code)
    tts.save(str(output_path))

    audio_url = f'http://127.0.0.1:5000/api/voice/file/{filename}'

    return {
        'audioUrl': audio_url,
        'filePath': str(output_path),
        'language': language_code,
    }