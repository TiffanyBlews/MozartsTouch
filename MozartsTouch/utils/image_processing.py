import os
import time
from pathlib import Path
from PIL import Image
import torch
from transformers import AutoModelForCausalLM, AutoProcessor
from loguru import logger

module_path = Path(__file__).resolve().parent.parent

class ImageRecognization:
    def __init__(self, beam_amount=7, min_prompt_length=15, max_prompt_length=30, test_mode=False):
        self.processor = None
        self.model = None
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32
        self.beam_amount = beam_amount
        self.min_length = min_prompt_length
        self.max_length = max_prompt_length
        self.test_mode = test_mode
        logger.info(f"self.device: {self.device}")
        if not self.test_mode:
            self._load_model("Florence-2-large")  # Call the _load_model method

    def _load_model(self, model_name="Florence-2-large"):
        if not self.model or not self.processor:
            logger.info(f"Loading captioning model {model_name}")
            start_time = time.time()
            self.processor = AutoProcessor.from_pretrained(module_path / "model" / f"{model_name}_processor", trust_remote_code=True)
            self.model = AutoModelForCausalLM.from_pretrained(
                module_path / "model" / f"{model_name}_model", torch_dtype=self.torch_dtype, trust_remote_code=True
            ).to(self.device)
            logger.info(f"[TIME] taken for loading {model_name}: {time.time() - start_time :.2f}s")

    def img2txt(self, image: Image, task='<MORE_DETAILED_CAPTION>') -> str:
        '''将图片转换为文本'''
        if self.test_mode:
            return self._test_img2txt()
        return self._img2txt(image, task)

    def _img2txt(self, image: Image, task='<MORE_DETAILED_CAPTION>') -> str:
        start_time = time.time()
        image = image.convert('RGB')
        inputs = self.processor(text=task, images=image, return_tensors="pt").to(self.device, self.torch_dtype)
        generated_ids = self.model.generate(
            input_ids=inputs["input_ids"],
            pixel_values=inputs["pixel_values"],
            max_new_tokens=1024,
            num_beams=self.beam_amount,
            do_sample=False
        )
        generated_text = self.processor.batch_decode(generated_ids, skip_special_tokens=False)[0]
        parsed_answer = self.processor.post_process_generation(generated_text, task=task, image_size=(image.width, image.height))
        logger.info(f"[TIME] taken for img2txt: {time.time() - start_time :.2f}s")
        logger.info(parsed_answer)
        return parsed_answer[task]

    def _test_img2txt(self) -> str:
        '''测试用函数，只会直接返回一种结果'''
        return "The image is a comic strip with four panels. \n\nThe first panel on the top left shows a young man with brown hair and a blue shirt, who appears to be a doctor or nurse. He is standing in front of a door with the word \"GENO\" written on it. The man is gesturing with his hand as if he is explaining something to the doctor.\n\nIn the second panel, there is a young woman sitting at a desk with a concerned expression on her face. She is looking at the doctor with a worried expression. The doctor is wearing a stethoscope around his neck and is holding a clipboard in his hand. The woman is lying on a hospital bed with her eyes closed and her head resting on the bed. The background shows a hospital room with a window and a door."

if __name__ == "__main__":
    test_image = module_path / "static" / "test.jpg"
    test_image = r"C:\Users\ljj\Downloads\VE7Z10AAOTyPsEDH2nspEXpURazGWgbjXxgbT4_UrR9fEcNQM672DkJqVDZ-p68zYRN832Wd18XpG0sySsNHOg.webp"

    image = Image.open(test_image)
    img_recog = ImageRecognization()
    for task in ['<CAPTION>', '<DETAILED_CAPTION>', '<MORE_DETAILED_CAPTION>']:
        result = img_recog.img2txt(image, task)