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


from utils.image_processing import img2txt, ci_config
from utils.text_processing import test, mubert, riffusion
ci = Interrogator(ci_config)

app_path = Path(__file__).parent
app = FastAPI()

async def Diancai(img, mode):
    txt = await img2txt(ci, img)

    mode_dict={
        0: test,
        1: mubert,
        2: riffusion
    }
    result = await mode_dict[mode](txt)

    return {'result': result}

async def get_bytes_from_url(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

@app.post("/upload")
async def create_upload_file(file: UploadFile = File(...)):
    img = file.file
    return await Diancai(img)

@app.post("/upload-url")
async def upload_url(*, url: str = Form(...)):
    bytes = await get_bytes_from_url(url)
    img = BytesIO(bytes)
    return await Diancai(img)

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)