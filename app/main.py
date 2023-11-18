from ast import Bytes
import base64
import datetime
from fastapi import FastAPI, File, UploadFile, Form
# from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from io import BytesIO
# import aiohttp
import asyncio
# from pydantic import BaseModel
from PIL import Image
from pydantic import BaseModel

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

#设定一个灵活转换类型的函数
def convert_to_bytes(data):
    if isinstance(data, bytes):
        # 如果data已经是bytes类型，则无需转换，直接返回
        return data
    elif isinstance(data, BytesIO):
        # 如果data是BytesIO类型，则调用getvalue()方法获取bytes数据
        return data.getvalue()
    else:
        raise ValueError("Invalid data type. Expected bytes or BytesIO.")

class Entry:

    def __init__(self, img: Image, image_recog:ImageRecognization, music_gen: MusicGenerator, time: int) -> None:
        self.img=img
        self.music_gen = music_gen
        self.image_recog = image_recog
        self.txt = None
        self.time = time
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    
    def img2txt(self):
        self.txt = self.image_recog.img2txt(self.img)
    
    def _test_img2txt(self):
        self.txt = self.image_recog._test_img2txt(self.img)

    def txt2music(self):
        self.music_bytes_io = self.music_gen.generate(self.txt, self.time)
        # self.music_b64 = base64.b64encode(music_bytes_io.getvalue()).decode()

    def save_to_file(self):
        output_folder = Path("outputs")
        output_folder.mkdir(parents=True, exist_ok=True)

        self.result_file = f"{self.timestamp}.mp3"
        file_path = output_folder / self.result_file

        with open(file_path, "wb") as music_file:
            music_file.write(convert_to_bytes(self.music_bytes_io))

        print(f"音乐已保存至 {file_path}")

        return self.result_file
        
class ResultModel(BaseModel):
    prompt: str
    result_file: str

async def Diancai(img: Image, mode: int, time: int):
    mg = mgfactory.create_generator(mode)

    entry = Entry(img, ir, mg, time)
    # 图片转文字
    if test_mode:
        entry._test_img2txt()
    else:
        entry.img2txt()
    # 文字生成音乐
    entry.txt2music()
    entry.save_to_file()
    result = ResultModel(prompt= entry.txt, result_file= entry.result_file)
    
    return result

def read_image_from_binary(binary: BytesIO) -> Image.Image:
    img = Image.open(binary)
    return img

'''
async def get_bytes_from_url(url: str):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.read()
'''

@app.post("/upload", response_model=ResultModel)
async def upload_file(file: UploadFile = File(...), mode: int = Form(...), time: int = Form(...)):
    '''
    上传图片以进行音乐生成

    Parameters:
    - file: 图片文件，Content-Type: image/*
    - mode: 指定生成模型（0:测试用；1:MusicGen模型）
    - time: 指定生成时间，请输入整数，以秒为单位

    Return: 
    - prompt: 图片转文字结果
    - result_file: 生成的音频文件名，使用GET方法访问"主机名/music/{result_file}"获取音频文件
    '''
    img = read_image_from_binary(file.file)
    return await Diancai(img, mode, time)

"""
@app.post("/upload-url", response_model=ResultModel)
async def upload_url(*, url: str = Form(...), mode: int = Form(...), time: int = Form(...)):
    '''
    上传图片链接以进行音乐生成

    Parameters:
    - url: 图片链接
    - mode: 指定生成模型（0:测试用；1:Mubert模型（不可用）；2:Riffusion模型（不可用）；3:MusicGen模型

    Return: 
    - prompt: 图片转文字结果
    - result_file: 生成的音频文件名，使用GET方法访问"主机名/music/{result_file}"获取音频文件
    '''
    bytes = await get_bytes_from_url(url)
    img = read_image_from_binary(BytesIO(bytes))
    return await Diancai(img, mode, time)
"""

@app.get("/")
async def root():
    return {"message": "Good morning, and in case I don't see you, good afternoon, good evening, and good night!"}

@app.get("/music/{result_file}")
async def get_music(result_file: str):
    '''
    下载对应位置的音频文件

    Return: 
    - 音频文件
    '''
    file_full_path = Path("outputs") / result_file
    return FileResponse(file_full_path)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=True)