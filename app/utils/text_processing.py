from pathlib import Path
import base64
app_path = Path(__file__).resolve().parent.parent

async def test(txt):
    test_path = app_path/"static"/"BONK.mp3"
    f = open(test_path)
    return base64.b64encode(f.read()).decode("utf-8")

async def mubert(txt):
    pass

async def riffusion(txt):
    pass
