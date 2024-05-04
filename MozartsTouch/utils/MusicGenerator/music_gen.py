from pathlib import Path
import time
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy
import torch
from io import BytesIO
device = 'cuda' if torch.cuda.is_available() else 'cpu'
app_path = Path(__file__).resolve().parent.parent.parent # app_path为项目根目录（`/app`）

class MusicGen:
    def __init__(self, model_name = "musicgen_small") -> None:
        self.processor = AutoProcessor.from_pretrained(app_path / "model" / (model_name+"_processor"))
        self.model = MusicgenForConditionalGeneration.from_pretrained(app_path / "model" / (model_name+"_model")).to(device)
        self.sampling_rate = self.model.config.audio_encoder.sampling_rate

    def generate(self, text: str, music_duration: int) -> BytesIO:
        '''
        使用 MusicGen 模型生成音乐
        '''
        start_time = time.time()

        inputs = self.processor(
            text=[text],
            padding=True,
            return_tensors="pt",
        ).to(device)
        audio_values = self.model.generate(**inputs, max_new_tokens=int(music_duration*256/5)) # music_duration为秒数，256token = 5s 

        # 将生成的音乐数据转换为BytesIO并返回
        wav_file_data = BytesIO()
        scipy.io.wavfile.write(wav_file_data, rate=self.sampling_rate, data=audio_values[0, 0].cpu().numpy())
        print(f"[TIME] taken for txt2music: {time.time() - start_time :.2f}s")
        return wav_file_data

if __name__=="__main__":    
    music_gen_small = MusicGen()
    output = music_gen_small.generate("cyberpunk electronic dancing music",1)
    with open(app_path / 'music_gen_test.wav', 'wb') as f:
        f.write(output.getvalue())
