import os
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from pydub import AudioSegment, silence

def process_audio_data(filename, audio_data, sample_rate, volume_boost):
    # Convert to 16-bit data
    audio_data_16bit = (audio_data * 32767).astype(np.int16)

    write(filename, sample_rate, audio_data_16bit)
    audio_segment = AudioSegment.from_wav(filename)
    audio_segment = audio_segment + volume_boost

    return audio_segment

def record_audio(chunk_duration):
    # Parameters
    output_name = 'output.wav'
    chunk_name = 'chunk.wav'
    sample_rate = 44100
    channels_number = 1
    silence_threshold = -32
    min_silence_len = 2000
    volume_boost = 6
    buffer_duration = 1  # Duration of buffer to add to the end of the recording

    # Initialize a buffer for the audio data
    audio_data = np.array([])
    status='Recording...'
    print(status)
    recorder = sd.InputStream(samplerate=sample_rate, channels=channels_number)
    recorder.start()

    while True:
        # Record audio for chunk_duration seconds
        chunk, _ = recorder.read(int(sample_rate * chunk_duration))
        audio_data = np.append(audio_data, chunk)
        chunk_segment = process_audio_data(chunk_name, chunk, sample_rate, volume_boost)

        # Detect silence in the chunk
        nonsilent_slices = silence.detect_nonsilent(chunk_segment, min_silence_len=min_silence_len, silence_thresh=silence_threshold)
        if not nonsilent_slices:
            status = 'Silence detected'
            print(status)
            break

    recorder.stop()
    status = 'Recording finished'
    print(status)

    audio_segment = process_audio_data(output_name, audio_data, sample_rate, volume_boost)
    audio_segment += AudioSegment.silent(duration=buffer_duration * 1000)

    audio_segment.export('question.mp3', format='mp3')
    os.remove(output_name)
    os.remove(chunk_name)
