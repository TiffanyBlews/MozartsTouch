import os

os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
from PIL import Image
# from clip_interrogator import Config, Interrogator
import torch
from pathlib import Path
import time
from transformers import AutoModelForCausalLM, AutoProcessor

import yaml
from loguru import logger

module_path = Path(__file__).resolve().parent.parent # module_path为模块根目录（`/MozartsTouch`）

class ImageRecognization:
    # TODO: 去掉clip_interrogator
    def __init__(self,
            beam_amount = 7,
            min_prompt_length = 15,
            max_prompt_length = 30) -> None:
        '''初始化图像识别配置'''
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        logger.info(f"self.device: {self.device}")
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

        self.beam_amount = beam_amount
        self.min_length = min_prompt_length
        self.max_length = max_prompt_length


    def load_model(self, model_name = "Florence-2-large"):
        logger.info(f"Loading BLIP model {model_name}")
        start_time = time.time()

        self.processor = AutoProcessor.from_pretrained(module_path / "model" / f"{model_name}_processor",trust_remote_code=True)
        self.model = AutoModelForCausalLM.from_pretrained(
            module_path / "model" / f"{model_name}_model", torch_dtype=torch.float16,trust_remote_code=True
        ).to(self.device)
        logger.info(f"[TIME] taken for loading {model_name}: {time.time() - start_time :.2f}s")


    def img2txt(self, image: Image, task='<MORE_DETAILED_CAPTION>') -> str:
        start_time = time.time()
        image = image.convert('RGB')
        inputs = self.processor(text=task, images=image, return_tensors="pt").to(self.device, self.torch_dtype)
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=3,
            do_sample=False
        )
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]

        parsed_answer = self.processor.post_process_generation(generated_text, task=task, image_size=(image.width, image.height))

        # inputs = self.processor(images=image, return_tensors="pt").to(self.device, torch.float16)
        # generated_ids = self.model.generate(
        #         **inputs, 
        #         num_beams=self.beam_amount, 
        #         min_length=self.min_length, 
        #         max_length=self.max_length
        #     )
        # generated_text = self.processor.batch_decode(
        #     generated_ids, 
        #     skip_special_tokens=True)[0].strip()
        
        logger.info(f"[TIME] taken for img2txt: {time.time() - start_time :.2f}s")
        logger.info(parsed_answer)
        return parsed_answer[task]

    def test_img2txt(self, image: Image) -> str:
        '''测试用函数，只会直接返回一种结果'''
        return "beautiful landscape of Africa, very satisfying, a lot of flowers and animals"

if __name__=="__main__":
    # 打开测试图像文件
    test_image = module_path / "static" / "test.jpg"
    image =Image.open(test_image)

    # 测试能否识别测试图像
    img_recog = ImageRecognization()
    img_recog.load_model()
    for task in ['<CAPTION>', '<DETAILED_CAPTION>', '<MORE_DETAILED_CAPTION>']:
        result = img_recog.img2txt(image, task)
        # print(result)