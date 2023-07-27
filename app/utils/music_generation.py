from ast import Bytes
from pathlib import Path
import base64
app_path = Path(__file__).resolve().parent.parent

from abc import ABCMeta, abstractmethod

class MusicGenerator(metaclass=ABCMeta):
    @abstractmethod
    def generate(self, text: str) ->Bytes:
        pass

class MusicGeneratorFactory:
    def create_generator(self, mode) -> MusicGenerator:
        generator_dict={
            0: TestGenerator,
            1: MubertGenerator,
            2: RiffusionGenerator
        }
        return generator_dict[mode]()

class TestGenerator(MusicGenerator):
    def generate(self, text: str) -> Bytes:
        print("音乐生成提示词：" + text)
        test_path = app_path/"static"/"BONK.mp3"
        test_mp3 = open(test_path,"rb").read()
        return test_mp3

class MubertGenerator(MusicGenerator):
    def generate(self, text: str) -> Bytes:
        pass

class RiffusionGenerator(MusicGenerator):
    def generate(self, text: str) -> Bytes:
        pass

class MousaiGenerator(MusicGenerator):
    def generate(self, text: str) -> Bytes:
        pass


if __name__=="__main__":
    mgfactory = MusicGeneratorFactory()
    mg = mgfactory.create_generator(0)
    print(mg.generate(""))