from pathlib import Path
import datetime
from PIL import Image
import time
import argparse
import yaml
from loguru import logger


'''
Because of Python's feature of chain importing (https://stackoverflow.com/questions/5226893/understanding-a-chain-of-imports-in-python)
you need to use these lines below instead of those above to be able to run the test code after `if __name__=="__main__"`
'''
if __name__=="__main__":
    from utils.image_processing import ImageRecognization
    from utils.music_generation import MusicGenerator,  MusicGeneratorFactory
    from utils.txt_converter import TxtConverter
    from utils.preprocess_single import PreProcessVideos
else: 
    from .utils.image_processing import ImageRecognization
    from .utils.music_generation import MusicGenerator,  MusicGeneratorFactory
    from .utils.txt_converter import TxtConverter
    from .utils.preprocess_single import PreProcessVideos


module_path = Path(__file__).resolve().parent 
with open(module_path / 'config.yaml', 'r', encoding='utf8') as file:
    config = yaml.safe_load(file)

test_mode = config['TEST_MODE']

def import_clip():
    '''导入图像识别模型'''
    start_time = time.time()

    ir = ImageRecognization()
    if not test_mode:
        ir.instantiate_ci()
    logger.info(f"[TIME] taken to load Image Recognition module: {time.time() - start_time :.2f}s")

    return ir

def import_music_generator():
    start_time = time.time()
    music_model = config['DEFAULT_MUSIC_MODEL']
    if test_mode:
        mg = MusicGeneratorFactory.create_music_generator("test")
    else:
        mg = MusicGeneratorFactory.create_music_generator(music_model)
    logger.info(f"[TIME] taken to load Music Generation module {music_model}: {time.time() - start_time :.2f}s")
    return mg


class Entry:
    '''每个Entry代表一次用户输入，然后调用自己的方法对输入进行处理以得到生成结果'''
    def __init__(self, img: Image, image_recog:ImageRecognization, music_gen: MusicGenerator,\
                  music_duration: int, addtxt:str) -> None:
        self.img=img
        self.txt = None
        self.txt_con = TxtConverter()
        self.converted_txt = None
        self.addtxt = addtxt # 追加文本输入
        self.image_recog = image_recog # 使用传入的图像识别模型对象
        self.music_gen = music_gen  # 使用传入的音乐生成对象
        self.music_duration = music_duration
        self.timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S") # 记录用户上传时间作为标识符
        self.result_urls = None
        self.music_bytes_io = None

    def img2txt(self):
        '''进行图像识别'''
        self.txt = self.image_recog.img2txt(self.img)
    
    def test_img2txt(self):
        '''测试用，跳过图像识别'''
        self.txt = self.image_recog.test_img2txt(self.img)
        
    def txt_converter(self):
        self.converted_txt = self.txt_con.txt_converter(self.txt, self.addtxt) # 追加一个附加输入，具体改动参见txt_converter

    def video_txt_descriper(self, texts):
        self.txt = self.txt_con.process_video_description(texts)

    def video_txt_converter(self):
        self.converted_txt = self.txt_con.video_txt_converter(self.txt, self.addtxt) # 追加一个附加输入，具体改动参见txt_converter

    def txt2music(self):
        '''根据文本进行音乐生成，获取生成的音乐的BytesIO或URL'''
        if self.music_gen.model_name.startswith("Suno"):
            self.result_urls = self.music_gen.generate(self.converted_txt, self.music_duration)
        else:
            self.music_bytes_io = self.music_gen.generate(self.converted_txt, self.music_duration)

    def save_to_file(self, output_folder:Path):
        '''将音乐保存到`/outputs`中，文件名为用户上传时间的时间戳'''
        output_folder.mkdir(parents=True, exist_ok=True)

        self.result_file_name = f"{self.timestamp}.wav"
        file_path = output_folder / self.result_file_name

        with open(file_path, "wb") as music_file:
            music_file.write(self.music_bytes_io.getvalue())

        logger.info(f"音乐已保存至 {file_path}")

        return self.result_file_name
    
def img_to_music_generate(img: Image, music_duration: int, image_recog: ImageRecognization, music_gen: MusicGenerator, output_folder=Path("./outputs"), addtxt: str=None):
    '''模型核心过程'''
    # 根据输入mode信息获得对应的音乐生成模型类的实例
    # mg = mgs[mode]

    # 根据用户输入创建一个类，并传入图像识别和音乐生成模型的实例
    entry = Entry(img, image_recog, music_gen, music_duration, addtxt)

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

    if not music_gen.model_name.startswith("Suno"):
        # print("Here.")
        entry.save_to_file(output_folder)

    return (entry.txt, entry.converted_txt, entry.result_file_name, music_gen.model_name)

def video_to_music_generate(video_path: str, music_duration: int, music_gen: MusicGenerator, output_folder=Path("./outputs"), addtxt: str=None):
    '''模型核心过程'''
    # 根据输入mode信息获得对应的音乐生成模型类的实例
    # mg = mgs[mode]

    # 根据用户输入创建一个类，并传入图像识别和音乐生成模型的实例
    entry = Entry(None, None, music_gen, music_duration, addtxt)

    videoBLIP = PreProcessVideos(video_path)
    video_frame_texts = videoBLIP.process_video()
    entry.video_txt_descriper(video_frame_texts)

    # 文本优化
    entry.video_txt_converter()

    #文本生成音乐
    entry.txt2music()
    entry.save_to_file(output_folder)

    return (entry.txt, entry.converted_txt, entry.result_file_name)
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Mozart\'s Touch: Multi-modal Music Generation Framework')

    parser.add_argument('-d', '--test', help='Test mode', default=False, action='store_true')
    parser.add_argument('-i', '--index', type=int, default=2, help='Music Generation Model: 1 - Suno, 2 - MusicGenSmall, 3 - MusicGenMedium')
    
    args = parser.parse_args()
    test_mode = args.test # True时关闭img2txt功能，节省运行资源，用于调试程序
    index = args.index

    image_recog = import_clip()
    music_gen = import_music_generator(index)

    output_folder = module_path / "outputs"
    img = Image.open(module_path / "static" / "test.jpg")
    music_duration =10
    addtxt = None

    key_names = ("prompt", "converted_prompt", "result_file_name")
    result = img_to_music_generate(img, music_duration, image_recog, music_gen, output_folder, addtxt)

    result_dict =  {key: value for key, value in zip(key_names, result)}

    logger.info(result_dict)