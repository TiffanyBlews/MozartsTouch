from transformers import AutoProcessor, MusicgenForConditionalGeneration

processor = AutoProcessor.from_pretrained("facebook/musicgen-medium")
model = MusicgenForConditionalGeneration.from_pretrained("facebook/musicgen-medium")


model.save_pretrained("./model/musicgen_medium_model")
processor.save_pretrained("./model/musicgen_medium_processor")
