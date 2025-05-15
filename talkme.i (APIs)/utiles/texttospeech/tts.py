# from flask import Flask, render_template, request, redirect, url_for
# import asyncio
# import edge_tts

# app = Flask(__name__)

# # Async function to generate audio
# async def text_to_speech(text, format="wav"):
#     filename = "output"  
#     communicate = edge_tts.Communicate(text, "hi-IN-SwaraNeural")
#     await communicate.save(f"{filename}.{format}")
#     return filename  # Return the generated filename

# # Home page with form to input text
# @app.route('/')
# def index():
#     return render_template('edge.html')

# # Endpoint to handle form submission
# @app.route('/generate_audio', methods=['POST'])
# def generate_audio():
#     text = request.form['text']
#     asyncio.run(text_to_speech(text))
#     return redirect(url_for('index'))

# if __name__ == "__main__":
#     app.run(debug=True)
from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import asyncio
import uvicorn
import edge_tts

app = FastAPI()
templates = Jinja2Templates(directory="templates")

# Async function to generate audio
async def text_to_speech(text, format="wav"):
    filename = "output"
    communicate = edge_tts.Communicate(text, "hi-IN-SwaraNeural")
    await communicate.save(f"{filename}.{format}")
    return filename  # Return the generated filename

# Home page with form to input text
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    return templates.TemplateResponse("edge.html", {"request": request})

# Endpoint to handle form submission
@app.post("/generate_audio")
async def generate_audio(text: str = Form(...)):
    await text_to_speech(text)
    return {"message": "Audio generation started successfully."}

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000)
