import os
from dotenv import load_dotenv
from utils import LanguageModel, TextSimilarity, write_to_file
from record import record_audio
from transcription import get_transcription
from pygame import mixer, time

def check_env_vars(*args):
    """Check if environment variables are set."""
    for var in args:
        if os.getenv(var) is None:
            raise Exception(f"Environment variable {var} is not set")

def initiate_chat(settings):
    # Check if environment variables are set
    check_env_vars('CLOUDFLARE_API', 'ELEVENLABS_API', 'CLOUDFLARE_ID')

    load_dotenv()
    cloudflare_model = settings["model"][1]
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
            {"role": "system", "content": f'''I am native English speaker.
            I do not mention who I am, unless the user prefers so.
            I try to answer to the user question and nothing else.
            I do not use any introduction and avoid not necessary comments.
            After answering I encourage the user to further conversation.
            I answer as concisely as I can, preferably in one sentence. 
            ```Context: {context}'''},
            {"role": "user", "content": f"{user_input}"}
        ],
        "max_tokens": 60
    }

    cloudflare_response = LanguageModel(
        f'{CLOUDFLARE_ENDPOINT}{cloudflare_model}', CLOUDFLARE_HEADERS, cloudflare_json
        ).get_response()
   
    assistant_answer = cloudflare_response.json()['result']['response']
   

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
