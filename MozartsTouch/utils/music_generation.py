import io
from pathlib import Path
from typing import Union

# from .MusicGenerator.MusicGeneratorType import MusicGenerator
# from .MusicGenerator.music_gen import MusicGen
# from .MusicGenerator.suno_ai import Suno
'''
Because of Python's feature of chain importing (https://stackoverflow.com/questions/5226893/understanding-a-chain-of-imports-in-python)
you need to use these lines below instead of those above to be able to run the test code after `if __name__=="__main__"`
'''
from MusicGenerator.MusicGeneratorType import MusicGenerator
from MusicGenerator.music_gen import MusicGen
from MusicGenerator.suno_ai import Suno


module_path = Path(__file__).resolve().parent.parent # module_path为模块根目录（`/MozartsTouch`）



class TestGenerator(MusicGenerator):
    def __init__(self) -> None:
        self._model_name = "test"
        print("Load TestGenerator")

    @property
    def model_name(self):
        return self._model_name

    def generate(self, text: str, music_duration: int) -> io.BytesIO:
        '''测试用，只会返回固定的*BONK*声音文件'''
        print("音乐生成提示词：" + text.encode('gbk', errors='replace').decode('gbk'))
        test_path = module_path/"static"/"BONK.mp3"
        test_mp3 = open(test_path,"rb").read()
        return io.BytesIO(test_mp3)



        
if __name__=="__main__":    
    music_gen_small = MusicGen("musicgen_small")
    output = music_gen_small.generate("cyberpunk electronic dancing music",1)
    print(music_gen_small.model_name)
    with open(module_path / 'musicgen.wav', 'wb') as f:
        f.write(output.getvalue())
