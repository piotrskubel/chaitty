import os
from dotenv import load_dotenv
from utils import LanguageModel

load_dotenv()
WHISPER_URL = f"https://api.cloudflare.com/client/v4/accounts/{os.getenv('CLOUDFLARE_ID')}/ai/run/@cf/openai/whisper"
WHISPER_HEADERS = {
    "Authorization": f"Bearer {os.getenv('CLOUDFLARE_API')}"
}

def get_transcription():

    with open('question.mp3', 'rb') as f:
        audio_data = f.read()

    whisper_response = LanguageModel(WHISPER_URL, WHISPER_HEADERS, audio_data).get_response(json_data=False)
    transcription = whisper_response.json()['result']['text']
    
    return transcription

