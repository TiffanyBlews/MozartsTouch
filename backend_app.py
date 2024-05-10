message = '''
不要直接运行这个程序！运行start_server.py！！！
Don't run this file directly! Run start_server.py instead!!!
'''
if __name__ == "__main__":
    print(message)

from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
# import uvicorn
from io import BytesIO
from PIL import Image
# from pydantic import BaseModel
from pathlib import Path
app_path = Path(__file__).parent # app_path为项目根目录（`/app`）
import MozartsTouch

class MusicGenerators: 
    '''惰性加载，需要用到哪个MusicGenerator再导入，同时记录下来，防止多次导入同一个模型'''
    music_gens = {}
    def get_music_gen(self, mode):
        if self.music_gens.keys().__contains__(mode):
            music_gen = self.music_gens[mode]
        else:
            music_gen = MozartsTouch.import_music_generator(mode)
            self.music_gens[mode] = music_gen
        return music_gen
        
mgs = MusicGenerators()
image_recog = MozartsTouch.import_clip()


# 创建后端应用
app = FastAPI(title='点彩成乐',description='“点彩成乐”项目后端')

origins = ["http://localhost:5173",
           "http://localhost:6006"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def read_image_from_binary(binary: BytesIO) -> Image.Image:
    '''将二进制输入转换为PIL Image对象'''
    img = Image.open(binary)
    return img

#上传部分主体

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), music_duration: int = Form(...), mode: int = Form(...)):
    '''
    上传图片以进行音乐生成

    Parameters:
    - file: 图片文件，Content-Type: image/*
    - music_duration: 指定生成时间，请输入整数，以秒为单位
    - mode: 0为测试模式，1为MusicGen-large，2为Suno-AI

    Return: 
    - prompt: 图片转文本结果
    - converted_prompt: 用于生成音乐的提示词文本
    - result_file_url: 生成的音频URL，使用GET方法访问"result_file_url"获取音频文件。
        如果使用Suno AI会一次生成两个音频，此时该值为字符串列表
    '''
    print("Request Received Successfully, Processing...")
    output_folder = app_path / "outputs"

    music_gen = mgs.get_music_gen(mode)

    img = read_image_from_binary(file.file)
    result = MozartsTouch.img_to_music_generate(img, music_duration, image_recog, music_gen, output_folder)

    key_names = ("prompt", "converted_prompt", "result_file_name", "mode")
    result_dict =  {key: value for key, value in zip(key_names, result)}
    print(result_dict)

    return result_dict


@app.get("/music/{result_file_name}")
async def get_music(result_file_name: str):
    '''
    获取/outputs目录下对应名称的文件

    Return: 
    - 音频文件
    '''
    file_full_path = app_path / "outputs" / result_file_name
    return FileResponse(file_full_path)

@app.get("/")
async def root():
    return {"message": "Good morning, and in case I don't see you, good afternoon, good evening, and good night! 这是“点彩成乐”后端域名，在域名后面加上`/docs#/`访问后端API文档页面！"}
