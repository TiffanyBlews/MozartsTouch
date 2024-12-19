from pathlib import Path
import time
from transformers import AutoProcessor, MusicgenForConditionalGeneration
import scipy.io.wavfile
import torch
from io import BytesIO
from loguru import logger

device = 'cuda' if torch.cuda.is_available() else 'cpu'
module_path = Path(__file__).resolve().parent.parent.parent

class MusicGen:
    def __init__(self, model_name="musicgen_small") -> None:
        self.processor = AutoProcessor.from_pretrained(module_path / "model" / f"{model_name}_processor")
        self.model = MusicgenForConditionalGeneration.from_pretrained(module_path / "model" / f"{model_name}_model").to(device)
        self.sampling_rate = self.model.config.audio_encoder.sampling_rate

    def generate(self, text: str, music_duration: int) -> BytesIO:
        logger.info(f"Start generating music")
        start_time = time.time()

        inputs = self.processor(
            text=[text],
            padding=True,
            return_tensors="pt",
        ).to(device)
        audio_values = self.model.generate(**inputs, max_new_tokens=int(256 * music_duration // 5)) # music_duration为秒数，256token = 5s 

        wav_file_data = BytesIO()
        scipy.io.wavfile.write(wav_file_data, rate=self.sampling_rate, data=audio_values[0, 0].cpu().numpy())
        logger.info(f"[TIME] taken for txt2music: {time.time() - start_time :.2f}s")
        return wav_file_data

if __name__ == "__main__":
    music_gen_small = MusicGen()
    output = music_gen_small.generate("cyberpunk electronic dancing music", 1)
    with open(module_path / 'music_gen_test.wav', 'wb') as f:
        f.write(output.getvalue())