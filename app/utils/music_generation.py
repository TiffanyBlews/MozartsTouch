import io
from pathlib import Path
import time

app_path = Path(__file__).resolve().parent.parent # app_path为项目根目录（`/app`）

from abc import ABC, abstractmethod

class MusicGenerator(ABC):
    '''
    音乐生成模型抽象基类，增加模型类时需要继承此类并实现generate方法
    详情请搜索面向对象编程，或参考https://python3-cookbook.readthedocs.io/zh-cn/latest/c08/p12_define_interface_or_abstract_base_class.html
    '''
    @abstractmethod
    def generate(self, text: str, music_duration: int) ->io.BytesIO:
        """
        根据传入文本和音乐时长生成音乐

        Parameters:
            text (str): 音乐生成的提示文本
            music_duration (int): 音乐的时长，单位为秒

        Returns:
            io.BytesIO: 包含生成音乐的字节流对象
        """
        pass

class MusicGeneratorFactory:
    '''
    为了便于测试调换模型，采用工厂模式获取音乐生成模型实例
    '''
    def create_generator(self, mode) -> MusicGenerator:
        '''获取音乐生成模型实例，0为测试，1为MusicGenSmall'''
        generator_dict={
            0: TestGenerator,
            1: MusicGenSmallGenerator
        }
        return generator_dict[mode]()

class TestGenerator(MusicGenerator):
    def generate(self, text: str, music_duration: int) -> io.BytesIO:
        '''测试用，只会返回固定的*BONK*声音文件'''
        print("音乐生成提示词：" + text.encode('gbk', errors='replace').decode('gbk'))
        test_path = app_path/"static"/"BONK.mp3"
        test_mp3 = open(test_path,"rb").read()
        return test_mp3

from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy

class MusicGenSmallGenerator(MusicGenerator):
    def __init__(self) -> None:
        
        self.processor = AutoProcessor.from_pretrained("./model/musicgen_small_processor")
        self.model = MusicgenForConditionalGeneration.from_pretrained("./model/musicgen_small_model")
        self.sampling_rate = self.model.config.audio_encoder.sampling_rate

    def generate(self, text: str, music_duration: int) -> io.BytesIO:
        '''
        使用 MusicGenSmall 模型生成音乐
        '''
        start_time = time.time()

        inputs = self.processor(
            text=[text],
            padding=True,
            return_tensors="pt",
        )
        audio_values = self.model.generate(**inputs, max_new_tokens=int(music_duration*256/5)) #music_duration为秒数，256token = 5s 

        # 将生成的音乐数据转换为BytesIO并返回
        wav_file_data = io.BytesIO()
        scipy.io.wavfile.write(wav_file_data, rate=self.sampling_rate, data=audio_values[0, 0].numpy())
        print(f"[TIME] taken for txt2music: {time.time() - start_time :.2f}s")
        return wav_file_data


if __name__=="__main__":
    # 测试能否正常生成音乐，保存到当前目录下
    mgfactory = MusicGeneratorFactory()
    mg = mgfactory.create_generator(1)
    output = mg.generate("cyberpunk electronic dancing music")
    with open('musicgen.wav', 'wb') as f:
        f.write(output.getvalue())
