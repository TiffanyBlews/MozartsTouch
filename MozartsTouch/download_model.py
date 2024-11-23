import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'

from pathlib import Path
from transformers import AutoProcessor, MusicgenForConditionalGeneration, BlipForConditionalGeneration

# 设置环境变量和路径
cwd = Path(__file__).resolve().parent
model_path = cwd / "model"
model_path.mkdir(parents=True, exist_ok=True)

# 通用加载和保存函数
def download_and_save_model(model_class, processor_class, model_name, save_dir):
    """
    下载模型和处理器并保存到指定路径
    :param model_class: 模型类
    :param processor_class: 处理器类
    :param model_name: 预训练模型名称
    :param save_dir: 保存目录
    """
    try:
        print(f"正在尝试加载模型和处理器: {model_name}...")
        model = model_class.from_pretrained(model_name)
        processor = processor_class.from_pretrained(model_name)
        save_folder = model_name.split("/")[-1]
        model.save_pretrained(save_dir / f"{save_folder}_model")
        processor.save_pretrained(save_dir / f"{save_folder}_processor")
        print(f"{model_name} 加载成功！")
    except Exception as e:
        print(f"下载 {model_name} 时出错: {e}")

# 下载模型
download_and_save_model(MusicgenForConditionalGeneration, AutoProcessor, "facebook/musicgen-small", model_path)
download_and_save_model(BlipForConditionalGeneration, AutoProcessor, "Salesforce/blip-image-captioning-base", model_path)
download_and_save_model(MusicgenForConditionalGeneration, AutoProcessor, "facebook/musicgen-medium", model_path)
