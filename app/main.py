from fastapi import FastAPI, File, UploadFile, Form
# from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from io import BytesIO
import aiohttp
import asyncio
# from pydantic import BaseModel
from PIL import Image

from utils.image_processing import ImageRecognization
from utils.music_generation import MusicGenerator, MusicGeneratorFactory

ir = ImageRecognization()
mgfactory = MusicGeneratorFactory()

test_mode = False # True时关闭img2txt功能，节省运行资源
if not test_mode:
    ir.instantiate_ci()

from pathlib import Path
app_path = Path(__file__).parent

app = FastAPI(title='点彩成乐',description='“点彩成乐”大创后端')
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class Entry:

    def __init__(self, img: Image, image_recog:ImageRecognization, music_gen: MusicGenerator) -> None:
        self.img=img
        self.music_gen = music_gen
        self.image_recog = image_recog
        self.txt = None
    
    def img2txt(self):
        self.txt = self.image_recog.img2txt(self.img)
    
    def _test_img2txt(self):
        self.txt = self.image_recog._test_img2txt(self.img)

    def txt2music(self):
        self.music_gen.generate(self.txt)


async def Diancai(img: Image, mode: int):
    mg = mgfactory.create_generator(mode)

    entry = Entry(img, ir, mg)
    # 图片转文字
    if test_mode:
        entry._test_img2txt()
    else:
        entry.img2txt()
    # 文字生成音乐

    result = entry.txt2music()

    return {'prompt': entry.txt, 'result': result}

def read_image_from_binary(binary: BytesIO) -> Image.Image:
    img = Image.open(binary)
    return img

async def get_bytes_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), mode: int = Form(...)):
    '''
    上传图片以进行音乐生成

    Parameters:
    - file: 图片文件，Content-Type: image/*
    - mode: 指定生成模型（0:测试用；1:Mubert模型；2:Riffusion模型）

    Return: 
    - prompt: 图片转文字结果
    - result: 生成的音频文件base64后的结果
    '''
    img = read_image_from_binary(file.file)
    return await Diancai(img, mode)

@app.post("/upload-url")
async def upload_url(*, url: str = Form(...), mode: int = Form(...)):
    '''
    上传图片链接以进行音乐生成

    Parameters:
    - url: 图片链接
    - mode: 指定生成模型（0:测试用；1:Mubert模型；2:Riffusion模型）

    Return: 
    - prompt: 图片转文字结果
    - result: 生成的音频文件base64后的结果
    '''
    bytes = await get_bytes_from_url(url)
    img = read_image_from_binary(BytesIO(bytes))
    return await Diancai(img, mode)

@app.get("/")
async def root():
    return {"message": "Good morning, and in case I don't see you, good afternoon, good evening, and good night!"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)