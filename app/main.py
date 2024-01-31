import datetime
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import uvicorn
from io import BytesIO
from PIL import Image
from pydantic import BaseModel
from pathlib import Path
import time

from utils.image_processing import ImageRecognization
from utils.music_generation import MusicGenerator, MusicGeneratorFactory

app_path = Path(__file__).parent# app_path为项目根目录（`/app`）

# 首先实例化模型，无论多少请求都只用同一个实例，这样只需导入模型一次即可

# 导入图像识别模型
start_time = time.time()

ir = ImageRecognization()
test_mode = False # True时关闭img2txt功能，节省运行资源，用于调试程序
if not test_mode:
    ir.instantiate_ci()

print(f"[TIME] taken to load Image Recognition model: {time.time() - start_time :.2f}s")

# 导入音乐生成模型
start_time = time.time()
mgfactory = MusicGeneratorFactory()
mgs = { 0:mgfactory.create_generator(0), 1: mgfactory.create_generator(1) }
print(f"[TIME] taken to load Music Generation model: {time.time() - start_time :.2f}s")

class Entry:
    '''每个Entry代表一次用户输入，然后调用自己的方法对输入进行处理以得到生成结果'''
    def __init__(self, img: Image, image_recog:ImageRecognization, music_gen: MusicGenerator, music_duration: int) -> None:
        self.img=img
        self.txt = None
        self.image_recog = image_recog # 使用传入的图像识别模型对象
        self.music_gen = music_gen  # 使用传入的音乐生成对象
        self.music_duration = music_duration
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # 记录用户上传时间作为标识符
    
    def img2txt(self):
        '''进行图像识别'''
        self.txt = self.image_recog.img2txt(self.img)
    
    def test_img2txt(self):
        '''测试用，跳过图像识别'''
        self.txt = self.image_recog.test_img2txt(self.img)

    def txt2music(self):
        '''根据文本进行音乐生成，获取生成的音乐的BytesIO'''
        self.music_bytes_io = self.music_gen.generate(self.txt, self.music_duration)

    def save_to_file(self):
        '''将音乐保存到`/outputs`中，文件名为用户上传时间的时间戳'''
        output_folder = Path("outputs")
        output_folder.mkdir(parents=True, exist_ok=True)

        self.result_file_name = f"{self.timestamp}.mp3"
        file_path = output_folder / self.result_file_name

        with open(file_path, "wb") as music_file:
            music_file.write(self.music_bytes_io.getvalue())

        print(f"音乐已保存至 {file_path}")

        return self.result_file_name
        
class ResultModel(BaseModel):
    '''定义响应体格式'''
    prompt: str
    result_file_name: str

async def Diancai(img: Image, mode: int, music_duration: int):
    '''模型核心过程'''
    # 根据输入mode信息获得对应的音乐生成模型类的实例
    mg = mgs[mode]

    # 根据用户输入创建一个类，并传入图像识别和音乐生成模型的实例（无论多少请求都只用同一个实例，只需导入模型一次即可）
    entry = Entry(img, ir, mg, music_duration)

    # 图片转文字
    if test_mode:
        # 测试模式跳过图像识别，使用默认文本
        entry.test_img2txt()
    else:
        entry.img2txt()

    # 文本生成音乐
    entry.txt2music()
    entry.save_to_file()
    result = ResultModel(prompt= entry.txt, result_file_name= entry.result_file_name)
    
    return result

def read_image_from_binary(binary: BytesIO) -> Image.Image:
    '''将二进制输入转换为PIL Image对象'''
    img = Image.open(binary)
    return img

# 创建后端应用
app = FastAPI(title='点彩成乐',description='“点彩成乐”大创后端')

# 使用CORS解决跨域问题，防止出现跨域代理错误
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
#上传部分主体

@app.post("/upload", response_model=ResultModel)
async def upload_file(file: UploadFile = File(...), mode: int = Form(...), music_duration: int = Form(...)):
    '''
    上传图片以进行音乐生成

    Parameters:
    - file: 图片文件，Content-Type: image/*
    - mode: 指定生成模型（0:测试用；1:MusicGen模型）
    - music_duration: 指定生成时间，请输入整数，以秒为单位

    Return: 
    - prompt: 图片转文字结果
    - result_file_name: 生成的音频文件名，使用GET方法访问"主机名/music/{result_file_name}"获取音频文件
    '''
    img = read_image_from_binary(file.file)
    return await Diancai(img, mode, music_duration)

@app.get("/music/{result_file_name}")
async def get_music(result_file_name: str):
    '''
    下载对应位置的音频文件

    Return: 
    - 音频文件
    '''
    file_full_path = Path("outputs") / result_file_name
    return FileResponse(file_full_path)

@app.get("/")
async def root():
    return {"message": "Good morning, and in case I don't see you, good afternoon, good evening, and good night! 这是“点彩成乐”后端域名，在域名后面加上`/docs#/`访问后端API文档页面！"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)