import os
from transformers import AutoProcessor, MusicgenForConditionalGeneration

#设定文件路径
model_path = "./model"

#如果模型文件不存在

if not os.path.exists(model_path):

    print("model do not exist!\n")

    #下载musicgen-small并保存
    processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")


    model.save_pretrained("./app/model/musicgen_small_model")
    processor.save_pretrained("./app/model/musicgen_small_processor")

    print("musicgen_small get daze\n")

    #下载musicgen-medium并保存
    processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
    model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium")


    model.save_pretrained("./app/model/musicgen_medium_model")
    processor.save_pretrained("./app/model/musicgen_medium_processor")

    print("musicgen_medium get daze\n")


