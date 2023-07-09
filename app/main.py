from fastapi import FastAPI, File, UploadFile, Form
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
# from fastapi.middleware.cors import CORSMiddleware
from pathlib import Path
from io import BytesIO
import aiohttp
import asyncio

path = Path(__file__).parent
app = FastAPI()

def img2txt(img):
    prediction = 1
    return prediction

def test(img):
    return path/"static"/"BONK.mp3"

def mubert(txt):
    pass

def riffusion(txt):
    pass

def Diancai(img, mode):

    txt = img2txt(img)

    mode_dict={
        0: test,
        1: mubert,
        2: riffusion
    }
    result = mode_dict[mode](txt)

    return {'result': result}

async def get_bytes_from_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

@app.post("/upload")
async def create_upload_file(file: UploadFile = File(...)):
    img = file.file
    return Diancai(img)

@app.post("/classify-url")
async def classify_url(*, url: str = Form(...)):
    bytes = await get_bytes_from_url(url)
    img = BytesIO(bytes)
    return Diancai(img)