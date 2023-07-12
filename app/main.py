from typing import BinaryIO
from fastapi import FastAPI, File, UploadFile, Form
# from fastapi.responses import HTMLResponse
# from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pathlib import Path
from io import BytesIO
import aiohttp
import asyncio
from clip_interrogator import Interrogator
# from pydantic import BaseModel
from PIL import Image

from utils.image_processing import img2txt, ci_config
from utils.text_processing import test, mubert, riffusion
ci = Interrogator(ci_config)

app_path = Path(__file__).parent
app = FastAPI()

async def Diancai(img: Image, mode: int):
    txt = img2txt(ci, img)

    mode_dict={
        0: test,
        1: mubert,
        2: riffusion
    }
    result = mode_dict[mode](txt)

    return {'prompt': txt, 'result': result}

def read_image_from_binary(binary: BytesIO) -> Image.Image:
    img = Image.open(binary)
    return img

async def get_bytes_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

@app.post("/upload")
async def create_upload_file(file: UploadFile = File(...), mode: int = Form(...)):
    img = Image.open(file.file)
    return await Diancai(img, mode)

@app.post("/upload-url")
async def upload_url(*, url: str = Form(...), mode: int = Form(...)):
    bytes = await get_bytes_from_url(url)
    img = Image.open(BytesIO(bytes))
    return await Diancai(img, mode)

@app.get("/")
async def root():
    return {"message": "Good morning, and in case I don't see you, good afternoon, good evening, and good night!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)