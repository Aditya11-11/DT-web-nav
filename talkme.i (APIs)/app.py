import os
import json
import requests
import torch
import asyncio
from datetime import datetime
from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from langchain_groq import ChatGroq
from transformers import AutoProcessor, AutoModelForSpeechSeq2Seq, pipeline
import edge_tts
from vosk import Model as VoskModel, KaldiRecognizer
import wave
import magic
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
# Enable CORS for all origins.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------------------------------------------------------------
# GLOBAL VARIABLES
# -----------------------------------------------------------------------------
API_KEY = "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"

# system_prompt holds two components: manual and URL (navigation commands)
system_prompt = {
    "manual": """ System Prompt for Saira (Dispatch and Tracking Assistant):

        You are Saira, a female support assistant for Talkme.ai, specializing in dispatch and tracking services. Your primary goal is to provide precise, helpful, and professional responses to user inquiries, focusing on assisting users to navigate the website and providing specific details about the website pages. You should follow these guidelines:

        1. Persona & Style:
        You speak as Saira, a friendly, warm, and professional assistant.

        Always greet users politely and thank them when appropriate.

        Be polite, humble, and professional in all interactions.

        Do not repeat your introduction or persona multiple times in a conversation.

        2. Role:
        Your main role is to assist users in navigating through the dispatch and tracking website and when you nevigate user to a page you can say okii i am nevigating you to the page and then the page name user asked you to nevigate  

        When asked about the website: Describe it as a dispatch and tracking software with features like order tracking, live location tracking, dispatch load management, etc.

        When asked about the homepage: Mention:

        Features: live tracking, load management, customer portal, and analytical dashboard.

        Mention the presence of thousands of active users.

        3. Navigation Focus:
        Customer Registration Form: If asked, redirect users to the customer registration form URL.

        Saved Search Criteria/Search Broker: Redirect users to the search broker URL.

        Location-related queries: Redirect users to the location URL.

        Load Search or Recommended Load: Redirect to the opportunities URL.

        Quick Routing or Driver Calculation: Redirect to the dispatch URL.

        Tracking-related queries: Navigate to the tracking panel URL.

        4. Response Guidelines:
        Provide short, concise, and precise answers.

        Only answer specific queries related to website navigation or the features of the website.

        Do not provide additional information unless explicitly asked.

        Do not answer out-of-context questions.

        Maintain a polite and professional tone.

        5. Data Interpretation:
        When the user asks for website-specific details, always redirect them to the appropriate URL.

        If the requested information is not found, clearly inform the user and offer further assistance.

        If a request is out of scope or unclear, apologize and offer assistance if possible.

        6. Limitations:
        Do not fabricate data or provide additional details that were not explicitly requested.

        If the user asks an irrelevant question, politely mention that you cannot answer and suggest they ask something related to the website.

        Do not include additional context or details unless specifically asked for.""",
    "url": None
}

# Global dictionary for navigation commands.
navigation_commands = {}

# -----------------------------------------------------------------------------
# SETUP: Speech-to-Text (using Whisper) and Text-to-Speech (using Edge TTS)
# -----------------------------------------------------------------------------
print("Loading Whisper model and processor...")
# processor = AutoProcessor.from_pretrained("openai/whisper-small")
# model = AutoModelForSpeechSeq2Seq.from_pretrained("openai/whisper-small")
# device = "cuda" if torch.cuda.is_available() else "cpu"
# model.to(device)

vosk_model = VoskModel(r"C:\Users\patel\Desktop\talkme.i_working\talkme.i copy\models\vosk-model-en-in-0.5")


# asr_pipeline = pipeline(
#     "automatic-speech-recognition",
#     model=model,
#     tokenizer=processor.tokenizer,
#     feature_extractor=processor.feature_extractor,
#     device=0 if torch.cuda.is_available() else -1,
# )

async def text_to_speech(text: str, filename: str = "static/output.wav"):
    communicate = edge_tts.Communicate(text, "hi-IN-SwaraNeural")
    await communicate.save(filename)
    return filename

# -----------------------------------------------------------------------------
# LLM HELPER FUNCTION (ChatGroq)
# -----------------------------------------------------------------------------
def generate_response(user_text: str) -> str:
    # Create a ChatGroq client with the provided API key.
    llm = ChatGroq(
        model="llama-3.1-8b-instant",  # Use a valid model name.
        api_key=API_KEY,
        temperature=0,
        max_tokens=None,
        timeout=None,
        max_retries=2,
    )
    # Build the combined system prompt:
    manual = system_prompt.get("manual") or ""
    url_comp = system_prompt.get("url") or ""
    combined_prompt = manual + "\n" + url_comp if manual and url_comp else manual or url_comp
    messages = [
        ("system", combined_prompt),
        ("human", user_text),
    ]
    ai_msg = llm.invoke(messages)
    return ai_msg.content

# -----------------------------------------------------------------------------
# API ENDPOINTS
# -----------------------------------------------------------------------------

@app.post("/api/set_navigation_commands")
async def set_navigation_commands_endpoint(data: dict):
    global navigation_commands, system_prompt
    if not data or not isinstance(data, dict):
        raise HTTPException(status_code=400, detail="Provide a JSON object mapping command names to URLs.")
    navigation_commands.update(data)
    nav_list = [f"{key}: {url}" for key, url in navigation_commands.items()]
    system_prompt["url"] = "Navigation Commands:\n" + "\n".join(nav_list)
    return {
        "message": "Navigation commands updated successfully.",
        "navigation_commands": navigation_commands,
        "system_prompt": system_prompt
    }

@app.get("/api/get_prompt")
async def get_combined_prompt():
    manual = system_prompt.get("manual") or ""
    url_comp = system_prompt.get("url") or ""
    combined_prompt = manual + "\n" + url_comp if manual and url_comp else manual or url_comp
    if not combined_prompt:
        raise HTTPException(status_code=404, detail="No system prompt has been set yet.")
    return {"system_prompt": combined_prompt}

@app.post("/chat")
async def chat_endpoint(data: dict):
    if not data or "human_message" not in data:
        raise HTTPException(status_code=400, detail="Please provide a 'human_message' field.")
    if not API_KEY:
        raise HTTPException(status_code=500, detail="API key not set. Use /api/set_api_key.")
    human_message = data["human_message"]
    try:
        ai_response = generate_response(human_message)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM invocation error: {e}")
    
    # Check for navigation commands.
    redirect_url = None
    lower_text = human_message.lower() + " " + ai_response.lower()
    for key, url in navigation_commands.items():
        if key.lower() in lower_text and ("navigate" in lower_text or "redirect" in lower_text):
            redirect_url = url
            break

    result = {"response": ai_response}
    if redirect_url:
        result["redirect_url"] = redirect_url
    return result

# @app.post("/voice_assistant")
# async def voice_assistant_endpoint(audio_file: UploadFile = File(...)):
#     if not audio_file:
#         raise HTTPException(status_code=400, detail="No audio file provided.")
#     temp_audio_path = "temp_input.wav"
#     contents = await audio_file.read()
#     with open(temp_audio_path, "wb") as f:
#         f.write(contents)
    
#     # Transcribe the audio using Whisper.
#     transcription_result = asr_pipeline(temp_audio_path)
#     user_transcript = transcription_result.get("text", "")
#     if not user_transcript:
#         raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
    
#     # Generate LLM response.
#     try:
#         llm_response = generate_response(user_transcript)
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"LLM invocation error: {e}")
    
#     # Check for navigation commands.
#     redirect_url = None
#     lower_text = user_transcript.lower() + " " + llm_response.lower()
#     for key, url in navigation_commands.items():
#         if key.lower() in lower_text and ("navigate" in lower_text or "redirect" in lower_text):
#             redirect_url = url
#             break

#     # Convert LLM response to speech.
#     tts_filename = "static/output.wav"
#     await text_to_speech(llm_response, tts_filename)

#     result = {
#         "transcription": user_transcript,
#         "response": llm_response,
#         "audio_url": "/static/output.wav"
#     }
#     if redirect_url:
#         result["redirect_url"] = redirect_url
#     return result



@app.post("/voice_assistant")
async def voice_assistant_endpoint(audio_file: UploadFile = File(...)):
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided.")
    print(audio_file)
    temp_audio_path = "temp_input.wav"
    contents = await audio_file.read()
    with open(temp_audio_path, "wb") as f:
        f.write(contents)
    
    # Transcribe the audio using Vosk.
    try:
        wf = wave.open(temp_audio_path, "rb")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error opening audio file: {e}")
    
    # Ensure audio is WAV format mono PCM.
    if wf.getnchannels() != 1 or wf.getsampwidth() != 2 or wf.getcomptype() != "NONE":
        raise HTTPException(status_code=400, detail="Audio file must be WAV format mono PCM.")
    
    rec = KaldiRecognizer(vosk_model, wf.getframerate())
    result_text = ""
    while True:
        data = wf.readframes(4000)
        if len(data) == 0:
            break
        if rec.AcceptWaveform(data):
            res = json.loads(rec.Result())
            result_text += res.get("text", "") + " "
    final_res = json.loads(rec.FinalResult())
    result_text += final_res.get("text", "")
    user_transcript = result_text.strip()

    if not user_transcript:
        raise HTTPException(status_code=500, detail="Failed to transcribe audio.")
    
    # Generate LLM response.
    try:
        llm_response = generate_response(user_transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM invocation error: {e}")
    
    # Check for navigation commands.
    redirect_url = None
    lower_text = user_transcript.lower() + " " + llm_response.lower()
    for key, url in navigation_commands.items():
        if key.lower() in lower_text and ("navigate" in lower_text or "redirect" in lower_text):
            redirect_url = url
            break

    # Convert LLM response to speech.
    tts_filename = "static/output.wav"
    await text_to_speech(llm_response, tts_filename)

    result = {
        "transcription": user_transcript,
        "response": llm_response,
        "audio_url": "/static/output.wav"
    }
    if redirect_url:
        result["redirect_url"] = redirect_url
    return result
@app.post("/voice_assistant")
async def voice_assistant_endpoint(audio_file: UploadFile = File(...)):
    # print(audio_file)
    if not audio_file:
        raise HTTPException(status_code=400, detail="No audio file provided.")

    temp_audio_path = "temp_input.wav"
    contents = await audio_file.read()
    
    with open(temp_audio_path, "wb") as f:
        f.write(contents)

    # Open the WAV file and check format
    try:
        with wave.open(temp_audio_path, "rb") as wf:
            channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            comp_type = wf.getcomptype()

            # Auto-convert to mono PCM 16-bit if needed
            if channels != 1 or sample_width != 2 or comp_type != "NONE":
                raise HTTPException(status_code=400, detail="Audio must be 16-bit mono PCM WAV.")

            rec = KaldiRecognizer(vosk_model, wf.getframerate())
            result_text = ""

            while True:
                data = wf.readframes(4000)
                if len(data) == 0:
                    break
                if rec.AcceptWaveform(data):
                    res = json.loads(rec.Result())
                    result_text += res.get("text", "") + " "

            final_res = json.loads(rec.FinalResult())
            result_text += final_res.get("text", "")
            user_transcript = result_text.strip()

            if not user_transcript:
                raise HTTPException(status_code=500, detail="Failed to transcribe audio.")

    except wave.Error as e:
        raise HTTPException(status_code=500, detail=f"Error processing audio: {e}")

    # Generate LLM response
    try:
        llm_response = generate_response(user_transcript)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM invocation error: {e}")

    # Check for navigation commands
    redirect_url = None
    lower_text = user_transcript.lower() + " " + llm_response.lower()
    for key, url in navigation_commands.items():
        if key.lower() in lower_text and ("navigate" in lower_text or "redirect" in lower_text):
            redirect_url = url
            break

    # Convert LLM response to speech
    tts_filename = "static/output.wav"
    await text_to_speech(llm_response, tts_filename)

    result = {
        "transcription": user_transcript,
        "response": llm_response,
        "audio_url": "/static/output.wav"
    }
    if redirect_url:
        result["redirect_url"] = redirect_url
    return result

# # async def voice_assistant_endpoint(audio_file: UploadFile = File(...)):
# @app.post("/voice_assistant")
# async def voice_assistant_endpoint(audio_file: UploadFile = File(...)):
#     print("🚀 Request Received!")  # Check if request reaches the function

#     try:
#         print(f"File Name: {audio_file.filename}")  # Check if file is detected
#         print(f"Content Type: {audio_file.content_type}")  # Verify Content-Type
        
#         contents = await audio_file.read()
#         print(f"File Size: {len(contents)} bytes")  # Check file size

#         return {"message": "File received", "size": len(contents)}

#     except Exception as e:
#         print(f"Error: {e}")
#         raise HTTPException(status_code=500, detail=f"Server Error: {str(e)}")
# -----------------------------------------------------------------------------
# RUN THE APP
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    if not os.path.exists("static"):
        os.makedirs("static")
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
