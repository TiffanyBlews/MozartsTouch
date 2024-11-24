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
app_path = Path(__file__).parent# app_path为项目根目录（`/`）
import MozartsTouch
import cv2 as cv
from loguru import logger


        
music_gen = MozartsTouch.import_music_generator()
image_recog = MozartsTouch.import_clip()


# 创建后端应用
app = FastAPI(title='点彩成乐',description='“点彩成乐”项目后端')

origins = ["http://localhost:5173"]

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
async def upload_file(file: UploadFile = File(...), music_duration: int = Form(...), mode: int = Form(...), instruction: str= Form(...)):
    '''
    上传图片以进行音乐生成

    Parameters:
    - file: 图片文件，Content-Type: image/*
    - music_duration: 指定生成时间，请输入整数，以秒为单位
    - mode: 0为测试模式，1为Suno AI，2为MusicGen-Small，3为MusicGen-Medium
    - instruction: 用户输入的限定文本

    Return: 
    - prompt: 图片转文本结果
    - converted_prompt: 用于生成音乐的提示词文本
    - result_file_url: 生成的音频URL，使用GET方法访问"result_file_url"获取音频文件。
        如果使用Suno AI会一次生成两个音频，此时该值为字符串列表
    '''
    logger.info("Request Received Successfully, Processing...")
    output_folder = app_path / "outputs"


    img = read_image_from_binary(file.file)
    result = MozartsTouch.img_to_music_generate(img, music_duration, image_recog, music_gen, output_folder)

    if not music_gen.model_name.startswith("suno"):
        prefix = 'http://localhost:3001/music/'  # 将musicgen生成的音乐文件名包装成URL
        filename_with_prefix = prefix + result[2]

        result = (*result[:2], filename_with_prefix)

    key_names = ("prompt", "converted_prompt", "result_file_url")
    
    result_dict =  {key: value for key, value in zip(key_names, result)}
    logger.info('**********FINAL RESULT**********')
    logger.info(result_dict)

    return result_dict

@app.post("/video")
async def upload_file(file: UploadFile = File(...), instruction: str = File(...)):

    logger.info("Request Received Successfully, Processing...")
    output_folder = app_path / "outputs"
    video_path  = app_path / "videos" / file.filename

    # 将视频保存至本地，然后读取视频帧
    contents = await file.read()
    with open(video_path, "wb") as f: 
        f.write(contents)

    # 读取视频时长
    vidcapture = cv.VideoCapture(str(video_path))
    fps = vidcapture.get(cv.CAP_PROP_FPS)
    totalNoFrames = vidcapture.get(cv.CAP_PROP_FRAME_COUNT)
    music_duration = totalNoFrames // fps

    result = MozartsTouch.video_to_music_generate(str(video_path), music_duration, music_gen, output_folder, instruction)

    key_names = ("prompt", "converted_prompt", "result_file_name")
    result_dict =  {key: value for key, value in zip(key_names, result)}

    logger.info('**********FINAL RESULT**********')
    logger.info(result_dict)

    return result_dict


@app.get("/music/{result_file_name}")
async def get_music(result_file_name: str):
    '''
    获取/outputs目录下对应名称的文件

    Return: 
    - 音频文件
    '''
    file_full_path = app_path / "outputs" / result_file_name
    logger.info(f'Return file {file_full_path}')
    return FileResponse(file_full_path)

@app.get("/")
async def root():
    return {"message": "Good morning, and in case I don't see you, good afternoon, good evening, and good night! 这是“点彩成乐”后端域名，在域名后面加上`/docs#/`访问后端API文档页面！"}
