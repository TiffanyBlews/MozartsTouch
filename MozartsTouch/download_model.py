import os
from pathlib import Path
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
cwd = Path(__file__).resolve().parent 

from transformers import AutoProcessor, MusicgenForConditionalGeneration

#设定文件路径
model_path = cwd / "model"
model_path.mkdir(parents=True, exist_ok=True)

#下载musicgen-small并保存
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")


model.save_pretrained("./model/musicgen_small_model")
processor.save_pretrained("./model/musicgen_small_processor")

print("musicgen_small get daze\n")

#下载musicgen-medium并保存
processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium")


model.save_pretrained("./model/musicgen_medium_model")
processor.save_pretrained("./model/musicgen_medium_processor")

print("musicgen_medium get daze\n")


