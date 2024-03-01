'''
不要直接运行这个程序！运行start_server.py！！！
Don't run this file directly! Run start_server.py instead!!!
'''
import datetime
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
#import uvicorn
from io import BytesIO
from PIL import Image
from pydantic import BaseModel
from pathlib import Path
import time as timi
import os

from utils.image_processing import ImageRecognization
from utils.music_generation import MusicGenerator, MusicGenGenerator
from utils.txt_converter import TxtConverter

app_path = Path(__file__).parent# app_path为项目根目录（`/app`）

test_mode = False # True时关闭img2txt功能，节省运行资源，用于调试程序

#模型选择：本地测试建议使用small，服务器测试建议使用medium，默认改为small方便所有人本地测试
music_gen_model_name = "musicgen_small" # "musicgen_medium" or "musicgen_small"

def import_clip():
    '''导入图像识别模型'''
    start_time = timi.time()

    ir = ImageRecognization()
    if not test_mode:
        ir.instantiate_ci()
    print(f"[TIME] taken to load Image Recognition model: {timi.time() - start_time :.2f}s")

    return ir

def import_musicgen():
    '''导入音乐生成模型'''
    start_time = timi.time()
    # mgfactory = MusicGeneratorFactory()
    mg = MusicGenGenerator(music_gen_model_name)
    print(f"[TIME] taken to load Music Generation model: {timi.time() - start_time :.2f}s")
    return mg

ir = import_clip()
mg = import_musicgen()

class Entry:
    '''每个Entry代表一次用户输入，然后调用自己的方法对输入进行处理以得到生成结果'''
    def __init__(self, img: Image, image_recog:ImageRecognization, music_gen: MusicGenerator, time: int) -> None:
        self.img=img
        self.txt = None
        self.txt_con = TxtConverter()
        self.converted_txt = None
        self.image_recog = image_recog # 使用传入的图像识别模型对象
        self.music_gen = music_gen  # 使用传入的音乐生成对象
        self.time = time
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # 记录用户上传时间作为标识符
    
    def img2txt(self):
        '''进行图像识别'''
        self.txt = self.image_recog.img2txt(self.img)
    
    def test_img2txt(self):
        '''测试用，跳过图像识别'''
        self.txt = self.image_recog.test_img2txt(self.img)
        
    def txt_filter(self):
        final_txt = ""
        result_list = self.txt.split(", ")
        it = 0
        for rel in result_list:
            # print(rel)
            it += 1        
            if it == 3 : continue # list[3] 表示图片来源，可丢弃
            if it == 2 :
                rel = rel.split(" by")[0]  # list[2] 表示图片创作者，一般都是瞎猜的，可丢弃
            final_txt += rel + ", "
        
        self.txt = final_txt[:-2]
        print("filtered_prompt result:"+self.txt.encode('gbk', errors='replace').decode('gbk'))

    def txt_converter(self):
        self.converted_txt = self.txt_con.txt_converter(self.txt)

    def txt2music(self):
        '''根据文本进行音乐生成，获取生成的音乐的BytesIO'''
        self.music_bytes_io = self.music_gen.generate(self.converted_txt, self.time)

    def save_to_file(self):
        '''将音乐保存到`/outputs`中，文件名为用户上传时间的时间戳'''
        output_folder = app_path / "outputs"
        output_folder.mkdir(parents=True, exist_ok=True)

        self.result_file = f"{self.timestamp}.mp3"
        file_path = output_folder / self.result_file

        with open(file_path, "wb") as music_file:
            music_file.write(self.music_bytes_io.getvalue())

        print(f"音乐已保存至 {file_path}")

        return self.result_file
        
class ResultModel(BaseModel):
    '''定义响应体格式'''
    prompt: str
    converted_prompt: str
    result_file: str

async def Diancai(img: Image, mode: int, time: int):
    '''模型核心过程'''
    # 根据输入mode信息获得对应的音乐生成模型类的实例
    # mg = mgs[mode]

    # 根据用户输入创建一个类，并传入图像识别和音乐生成模型的实例（无论多少请求都只用同一个实例，只需导入模型一次即可）
    entry = Entry(img, ir, mg, time)

    # 图片转文字
    if test_mode:
        # 测试模式跳过图像识别，使用默认文本
        entry.test_img2txt()
    else:
        entry.img2txt()

    # 文本优化
    entry.txt_filter()
    entry.txt_converter()

    #文本生成音乐
    entry.txt2music()
    entry.save_to_file()
    result = ResultModel(prompt= entry.txt, converted_prompt= entry.converted_txt, result_file= entry.result_file)
    
    return result

def read_image_from_binary(binary: BytesIO) -> Image.Image:
    '''将二进制输入转换为PIL Image对象'''
    img = Image.open(binary)
    return img

# 创建后端应用
app = FastAPI(title='点彩成乐',description='“点彩成乐”大创后端')

# 使用CORS解决跨域问题，防止出现跨域代理错误
origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#上传部分主体

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
    print("Request Received Successfully, Processing...")
    img = read_image_from_binary(file.file)
    return await Diancai(img, mode, time)


@app.get("/music/{result_file}")
async def get_music(result_file: str):
    '''
    下载对应位置的音频文件

    Return: 
    - 音频文件
    '''
    file_full_path = os.path.join(app_path, "outputs", result_file)
    print("Here is ", file_full_path)
    return FileResponse(file_full_path)

@app.get("/")
async def root():
    return {"message": "Good morning, and in case I don't see you, good afternoon, good evening, and good night! 这是“点彩成乐”后端域名，在域名后面加上`/docs#/`访问后端API文档页面！"}

#if __name__ == "__main__":
    # uvicorn.run("main:app", host="0.0.0.0", port=3000, reload=False)
