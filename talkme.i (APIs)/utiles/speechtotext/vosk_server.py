import json
import pyaudio
from vosk import Model, KaldiRecognizer

# Paths to the models
model_path_en = r"C:\Users\patel\Desktop\talkme.i\utiles\speechtotext\models\vosk-model-en-in-0.5"
model_path_hi = r"C:\Users\patel\Desktop\talkme.i\utiles\speechtotext\models\vosk-model-hi-0.22"

# Load models
models = {
    "en": Model(model_path_en),
    "hi": Model(model_path_hi),
}

def speech_to_text(language: str = "en", prints: bool = True):
    """ Convert speech to text using the selected language model. """
    
    if language not in models:
        print("Invalid language selection. Defaulting to English.")
        language = "en"

    recognizer = KaldiRecognizer(models[language], 16000)
    print(f"Model Initialized for {language.upper()}...")

    # Initialize PyAudio
    audio = pyaudio.PyAudio()
    stream = audio.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
    stream.start_stream()

    try:
        while True:
            data = stream.read(4096, exception_on_overflow=False)
            if recognizer.AcceptWaveform(data):
                result = recognizer.Result()
                result_dict = json.loads(result)
                if 'text' in result_dict and result_dict['text'].strip():
                    if prints:
                        print("\rTranscript:", result_dict['text'])
                    yield result_dict['text'].lower()
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    selected_language = input("Enter language (en/hi): ").strip().lower()
    for speech in speech_to_text(language=selected_language):
        if "stop" in speech:
            print("Speech:", speech)
            print("Broken....")
            break
