from PIL import Image
from clip_interrogator import Config, Interrogator
import torch.cuda
from pathlib import Path
import time

app_path = Path(__file__).resolve().parent.parent

class ImageRecognization:
    def __init__(self) -> None:
        ci_config = Config()
        ci_config.clip_model_name = "ViT-H-14/laion2b_s32b_b79k"
        ci_config.caption_model_name = "blip-base"
        ci_config.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        ci_config.blip_offload = False if torch.cuda.is_available() else True
        ci_config.chunk_size = 1024
        ci_config.flavor_intermediate_count = 1024
        self.ci_config = ci_config
        

    def instantiate_ci(self):
        self.ci = Interrogator(self.ci_config)

    def img2txt(self, image: Image) -> str:
        start_time = time.time()
        image = image.convert('RGB')
        prompt_result = self.ci.interrogate_classic(image)

        print("[TIME] taken for img2txt (sec):", time.time() - start_time)
        print("prompt result:"+prompt_result.encode('gbk', errors='replace').decode('gbk'))
        return prompt_result

    def _test_img2txt(self, image: Image) -> str:
        return "beautiful landscape of Africa, very satisfying"

if __name__=="__main__":
    test_image = app_path / "static" / "test.jpg"
    image =Image.open(test_image)

    img_recog = ImageRecognization()
    img_recog.instantiate_ci()
    result = img_recog.img2txt(image)
    # print(result)