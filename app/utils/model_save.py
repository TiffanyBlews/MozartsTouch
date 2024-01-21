from transformers import AutoProcessor, MusicgenForConditionalGeneration

#下载musicgen-small并保存
processor = AutoProcessor.from_pretrained("facebook/musicgen-small")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-small")


model.save_pretrained("./model/musicgen_small_model")
processor.save_pretrained("./model/musicgen_small_processor")


#下载musicgen-medium并保存
processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium")


model.save_pretrained("./model/musicgen_medium_model")
processor.save_pretrained("./model/musicgen_medium_processor")
