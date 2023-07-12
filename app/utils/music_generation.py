from ast import Bytes
from pathlib import Path
import base64
app_path = Path(__file__).resolve().parent.parent

def test_music_gen(txt: str) -> Bytes:
    print("音乐生成提示词：" + txt)
    test_path = app_path/"static"/"BONK.mp3"
    test_mp3 = open(test_path,"rb").read()
    return base64.b64encode(test_mp3)

def mubert(txt: str) -> Bytes:
    pass

def riffusion(txt: str) -> Bytes:
    pass

if __name__=="__main__":
    print(test(""))