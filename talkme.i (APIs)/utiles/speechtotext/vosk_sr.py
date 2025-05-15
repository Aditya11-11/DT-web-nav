import json
import pyaudio
from vosk import Model, KaldiRecognizer
from typing import Generator

model_path: str = r"C:\Users\patel\Desktop\talkme.i\utiles\speechtotext\models\vosk-model-en-in-0.5"
# model_path: str = r"/Users/mac/Desktop/model/vosk-model-hi-0.22"
model = Model(model_path)
recognizer = KaldiRecognizer(model, 16000)

def speech_to_text(prints: bool = True) -> Generator[str, None, None]:
    print("Model Initialized....")

    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()

    try:
        while True:
            data = stream.read(4096, exception_on_overflow=False)  # Avoid overflow exceptions
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_dict = json.loads(result)
                if 'text' in result_dict:
                    if prints: print("\rTranscript: " + result_dict['text'])
                    yield result_dict['text'].lower()
            else:
                partial_result = recognizer.PartialResult()
                partial_dict = json.loads(partial_result)
                if 'partial' in partial_dict:
                    if prints: print("\rSpeaking: " + partial_dict['partial'], end='', flush=True)
                    yield partial_dict['partial'].lower()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Clean up
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    for speech in speech_to_text():
        if "stop" in speech:
            print("Speech: ", speech)  # The actual printing is handled within the function now
            print("Broken....")
            break