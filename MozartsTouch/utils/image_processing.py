from PIL import Image
from clip_interrogator import Config, Interrogator
import torch.cuda
from pathlib import Path
import time

app_path = Path(__file__).resolve().parent.parent # app_path为项目根目录（`/app`）

class ImageRecognization:
    def __init__(self) -> None:
        '''初始化图像识别配置'''
        ci_config = Config()
        ci_config.clip_model_name = "ViT-H-14/laion2b_s32b_b79k"
        ci_config.caption_model_name = "blip-large"
        ci_config.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        ci_config.blip_offload = False if torch.cuda.is_available() else True
        ci_config.chunk_size = 1024
        ci_config.flavor_intermediate_count = 1024
        self.ci_config = ci_config
        

    def instantiate_ci(self):
        '''实例化 Clip 模型的 Interrogator 对象，返回Interrogator实例'''
        self.ci = Interrogator(self.ci_config)

    def img2txt(self, image: Image) -> str:
        '''输入Image对象进行图像识别，输出并返回识别结果'''
        
        start_time = time.time()

        # 图像预处理
        image = image.convert('RGB')
        
        # 使用 Interrogator 对象进行图像识别
        prompt_result = self.ci.interrogate_classic(image)

        print(f"[TIME] taken for img2txt: {time.time() - start_time :.2f}s")
        print("prompt result:"+prompt_result.encode('gbk', errors='replace').decode('gbk'))
        return prompt_result

    def test_img2txt(self, image: Image) -> str:
        '''测试用函数，只会直接返回一种结果'''
        return "beautiful landscape of Africa, very satisfying, a lot of flowers and animals"
    
    def video2txt(self, video_path: str) -> str:
        start_time = time.time()

        # 图像预处理
        image = image.convert('RGB')
        
        # 使用 Interrogator 对象进行图像识别
        prompt_result = self.ci.interrogate_classic(image)

        print(f"[TIME] taken for img2txt: {time.time() - start_time :.2f}s")
        print("prompt result:"+prompt_result.encode('gbk', errors='replace').decode('gbk'))
        return prompt_result

if __name__=="__main__":
    # 打开测试图像文件
    test_image = app_path / "static" / "test.jpg"
    image =Image.open(test_image)

    # 测试能否识别测试图像
    img_recog = ImageRecognization()
    img_recog.instantiate_ci()
    result = img_recog.img2txt(image)
    # print(result)