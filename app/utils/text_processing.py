from pathlib import Path
app_path = Path(__file__).resolve().parent.parent

async def test(txt):
    return app_path/"static"/"BONK.mp3"

async def mubert(txt):
    pass

async def riffusion(txt):
    pass
