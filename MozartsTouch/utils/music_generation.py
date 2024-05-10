import io
from pathlib import Path
from typing import Tuple

from .MusicGenerator.music_gen import MusicGen
from .MusicGenerator.suno_ai import Suno

'''
Because of Python's feature of chain importing (https://stackoverflow.com/questions/5226893/understanding-a-chain-of-imports-in-python)
you need to use these lines below instead of those above to be able to run the test code after `if __name__=="__main__"`
'''
# from MusicGenerator.music_gen import MusicGen
# from MusicGenerator.suno_ai import Suno


app_path = Path(__file__).resolve().parent.parent # app_path为项目根目录（`/app`）

from abc import ABC, abstractmethod


class AbstractSingletonMeta(type, ABC):
    '''
    单例模式抽象基类元类，保证音乐生成类只有一个实例
    '''
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]
    

class MusicGenerator(metaclass=AbstractSingletonMeta):
    '''
    音乐生成模型抽象基类，增加模型类时需要继承此类并实现generate方法
    '''
    @property
    @abstractmethod
    def model_name(self):
        pass
    
    @abstractmethod
    def generate(self, text: str, music_duration: int):
        """
        根据传入文本和音乐时长生成音乐

        Parameters:
            text (str): 音乐生成的提示文本
            music_duration (int): 音乐的时长，单位为秒

        Returns:
            io.BytesIO: 包含生成音乐的字节流对象
        """
        pass

        

class TestGenerator(MusicGenerator):
    def __init__(self) -> None:
        self._model_name = "test"

    @property
    def model_name(self):
        return self._model_name

    def generate(self, text: str, music_duration: int) -> io.BytesIO:
        '''测试用，只会返回固定的*BONK*声音文件'''
        print("音乐生成提示词：" + text.encode('gbk', errors='replace').decode('gbk'))
        test_path = app_path/"static"/"BONK.mp3"
        test_mp3 = open(test_path,"rb").read()
        return io.BytesIO(test_mp3)


class MusicGenLargeGenerator(MusicGenerator):
    def __init__(self) -> None:
        self.model = MusicGen("musicgen-large")
        self._model_name = "musicgen-large"
    
    @property
    def model_name(self):
        return self._model_name

    def generate(self, text: str, music_duration: int) -> io.BytesIO:
        return self.model.generate(text, music_duration)
    
class MusicGenMediumGenerator(MusicGenerator):
    def __init__(self) -> None:
        self.model = MusicGen("musicgen-medium")
        self._model_name = "musicgen-medium"

    @property
    def model_name(self):
        return self._model_name
    
    def generate(self, text: str, music_duration: int) -> io.BytesIO:
        return self.model.generate(text, music_duration)


class SunoGenerator(MusicGenerator):
    def __init__(self) -> None:
        self._model_name = "Suno"
        pass

    @property
    def model_name(self):
        return self._model_name
    
    def generate(self, text: str, music_duration: int):
        return Suno.generate(text)


class MusicGeneratorFactory:
    '''
    为了便于测试调换模型，采用工厂模式获取音乐生成模型实例
    '''
    generator_classes = {
        "test": TestGenerator,
        "musicgen-large": MusicGenLargeGenerator,
        "musicgen-medium": MusicGenMediumGenerator,
        "suno.ai": SunoGenerator,
    }

    @classmethod
    def create_music_generator(cls, music_gen_model_name: str) -> MusicGenerator:
        generator_class = cls.generator_classes.get(music_gen_model_name)
        if generator_class:
            return generator_class()
        else:
            raise ValueError("Unsupported music_gen_model_name")

music_gen_small = MusicGeneratorFactory.create_music_generator("musicgen-large")

if __name__=="__main__":    

    output = music_gen_small.generate("cyberpunk electronic dancing music", 1)
    print(music_gen_small.model_name)
    with open(app_path / 'musicgen.wav', 'wb') as f:
        f.write(output.getvalue())
