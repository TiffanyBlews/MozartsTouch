
from PIL import Image
from clip_interrogator import Config, Interrogator
import torch
from pathlib import Path

app_path = Path(__file__).resolve().parent.parent

config = Config()
config.clip_model_name = "ViT-H-14/laion2b_s32b_b79k"
config.caption_model_name = "blip-base"
config.device = 'cuda' if torch.cuda.is_available() else 'cpu'
config.blip_offload = False if torch.cuda.is_available() else True
config.chunk_size = 1024
config.flavor_intermediate_count = 1024
ci = Interrogator(config)

def img2txt(image):
    image =Image.open(image)
    image = image.convert('RGB')
    prompt_result = ci.interrogate_fast(image)
    return prompt_result

if __name__=="__main__":
    test_image = app_path / "static" / "test.jpg"
    print("111")
    image =Image.open(test_image)
    image = image.convert('RGB')
    image.show()
    print(img2txt(test_image))