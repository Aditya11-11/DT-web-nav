# Load model directly
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq, pipeline
import torch

# Load processor and model
processor = AutoProcessor.from_pretrained("openai/whisper-small")
model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-small")

# Set the model to inference mode and configure device (CPU or GPU if available)
device = "cuda" if torch.cuda.is_available() else "cpu"
model.to(device)

# Create ASR pipeline
asr_pipeline = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    device=device,
)

# Path to audio file (you can replace with your actual file path)
audio_file = "path/to/your/audio/file.wav"

# Transcribe
result = asr_pipeline(audio_file)

# Print result
print("Transcription:", result["text"])
