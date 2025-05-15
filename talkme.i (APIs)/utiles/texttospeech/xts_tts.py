from fastapi.responses import FileResponse
from fastapi import FastAPI
from TTS.api import TTS 
import torch 
import soundfile
from transformers import VitsModel , AutoTokensiser 
import uvicorn
import os

app=FastAPI