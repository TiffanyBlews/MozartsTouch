from pathlib import Path
from .utils.image_processing import ImageRecognization
from .utils.music_generation import MusicGenerator, MusicGenGenerator, TestGenerator
from .utils.txt_converter import TxtConverter
import datetime
from PIL import Image
import time

test_mode = False # True时关闭img2txt功能，节省运行资源，用于调试程序


#模型选择：本地测试建议使用small，服务器测试建议使用medium，默认改为small方便所有人本地测试
music_gen_model_name = "musicgen_small" # "musicgen_medium" or "musicgen_small" or "test"

def import_clip():
    '''导入图像识别模型'''
    start_time = time.time()

    ir = ImageRecognization()
    if not test_mode:
        ir.instantiate_ci()
    print(f"[TIME] taken to load Image Recognition module: {time.time() - start_time :.2f}s")

    return ir

def import_musicgen():
    '''导入音乐生成模型'''
    start_time = time.time()
    if test_mode:
        mg = TestGenerator(music_gen_model_name)
    else:
        mg = MusicGenGenerator(music_gen_model_name)
    print(f"[TIME] taken to load Music Generation module: {time.time() - start_time :.2f}s")
    return mg


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
        
    def txt_converter(self):
        self.converted_txt = self.txt_con.txt_converter(self.txt)

    def txt2music(self):
        '''根据文本进行音乐生成，获取生成的音乐的BytesIO'''
        self.music_bytes_io = self.music_gen.generate(self.converted_txt, self.time)

    def save_to_file(self, output_folder:Path):
        '''将音乐保存到`/outputs`中，文件名为用户上传时间的时间戳'''
        output_folder.mkdir(parents=True, exist_ok=True)

        self.result_file_name = f"{self.timestamp}.wav"
        file_path = output_folder / self.result_file_name

        with open(file_path, "wb") as music_file:
            music_file.write(self.music_bytes_io.getvalue())

        print(f"音乐已保存至 {file_path}")

        return self.result_file_name
    
def MozartsTouch(img: Image, time: int, image_recog: ImageRecognization, music_gen: MusicGenerator, output_folder=Path("./output")):
    '''模型核心过程'''
    # 根据输入mode信息获得对应的音乐生成模型类的实例
    # mg = mgs[mode]

    # 根据用户输入创建一个类，并传入图像识别和音乐生成模型的实例
    entry = Entry(img, image_recog, music_gen, time)

    # 图片转文字
    if test_mode:
        # 测试模式跳过图像识别，使用默认文本
        entry.test_img2txt()
    else:
        entry.img2txt()

    # 文本优化
    entry.txt_converter()

    #文本生成音乐
    entry.txt2music()
    entry.save_to_file(output_folder)
    
    return (entry.txt, entry.converted_txt, entry.result_file_name)

if __name__ == "__main__":
    pass