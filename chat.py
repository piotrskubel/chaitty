import os
from dotenv import load_dotenv
from utils import LanguageModel, TextSimilarity, write_to_file, countdown
from record import record_audio
from transcription import get_transcription
from pygame import mixer, time


def check_env_vars(*args):
    """Check if environment variables are set."""
    for var in args:
        if os.getenv(var) is None:
            raise Exception(f"Environment variable {var} is not set")


def initiate_chat(settings):
   
    check_env_vars('CLOUDFLARE_API', 'ELEVENLABS_API', 'CLOUDFLARE_ID')

    load_dotenv()
    cloudflare_model = settings["model"][1]
    cloudflare_sentiment = "@cf/huggingface/distilbert-sst-2-int8"
    CLOUDFLARE_ENDPOINT = f"https://api.cloudflare.com/client/v4/accounts/{os.getenv('CLOUDFLARE_ID')}/ai/run/"
    CLOUDFLARE_HEADERS = {"Authorization": f"Bearer {os.getenv('CLOUDFLARE_API')}"}
    elevenlabs_voice = settings["voice"][1]
    ELEVENLABS_CHUNK = 1024
    ELEVENLABS_ENDPOINT = f"https://api.elevenlabs.io/v1/text-to-speech/"
    ELEVENLABS_HEADERS = {
    "Accept": "audio/mpeg",
    "Content-Type": "application/json",
    "xi-api-key": os.getenv('ELEVENLABS_API')
    }
    CONTEXT_STORAGE = "context.txt"
    
    record_audio(settings["silence"])

    user_input = get_transcription()
    write_to_file(CONTEXT_STORAGE, f'User: {user_input}')
    context = TextSimilarity().prepare_context(CONTEXT_STORAGE, user_input)
    cloudflare_json = {
            "messages": [
                {"role": "system", "content": f'''
                 <<SYS>>You chat with the user with one short sentence
                 and encourage the user to further chat with another short sentence.
                 Exception: when user wants to end the chat you say goodbye to the user.<</SYS>>
                 ###
                 Chat history: {context}'''},
                {"role": "user", "content": f'[INST]Always answer to this: {user_input}[/INST]'}
            ],
        }

    cloudflare_response = LanguageModel(
        f'{CLOUDFLARE_ENDPOINT}{cloudflare_model}', CLOUDFLARE_HEADERS, cloudflare_json
        ).get_response()

    assistant_answer = cloudflare_response.json()['result']['response']

    ending_json =  {
        "text" : user_input,
        }

    ending_response = LanguageModel(
        f'{CLOUDFLARE_ENDPOINT}{cloudflare_sentiment}', CLOUDFLARE_HEADERS, ending_json
        ).get_response()
    
    if ending_response.json()['result'][0]['score'] > ending_response.json()['result'][1]['score']:
        print('Chat will end soon')
        settings["auto_continue"] = False

    write_to_file(CONTEXT_STORAGE, f'Assistant: {assistant_answer}')
    elevenlabs_json = {
        "text": assistant_answer,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }
    elevenlabs_response = LanguageModel(
        f'{ELEVENLABS_ENDPOINT}{elevenlabs_voice}', ELEVENLABS_HEADERS, elevenlabs_json
        ).get_response()

    audio_answer = 'answer.mp3'
    audio_question = 'question.mp3'
    with open(audio_answer, 'wb') as f:
        for chunk in elevenlabs_response.iter_content(chunk_size=ELEVENLABS_CHUNK):
            if chunk:
                f.write(chunk)

    mixer.init()
    mixer.music.load(audio_answer)
    mixer.music.play()

    while mixer.music.get_busy():
        time.Clock().tick(10)
    mixer.quit()

    os.remove(audio_answer)
    os.remove(audio_question)
    if settings["auto_continue"]:
        countdown(3)
