from io import BytesIO
import numpy as np
from pydub import AudioSegment
from pathlib import Path

module_path = Path(__file__).resolve().parent.parent # module_path为模块根目录（`/MozartsTouch`）

def normalize_volume(audio_path):
    # 读取BytesIO对象中的音频数据
    audio_segment = AudioSegment.from_file(audio_path, format="mp3")  # 根据实际情况选择正确的格式

    # 将音频数据转换为numpy数组
    samples = np.array(audio_segment.get_array_of_samples())

    # 计算音频数据的最大振幅
    max_amplitude = np.max(np.abs(samples))
    print(max_amplitude)

    # 设置目标最大振幅    
    target_amplitude = 32000.0

    # 计算缩放因子
    scale_factor = target_amplitude / max_amplitude
    print(scale_factor)
    # 缩放音频数据
    normalized_samples = (samples * scale_factor).astype(np.int16)

    # 创建新的音频段并返回
    normalized_audio = AudioSegment(
        normalized_samples.tobytes(),
        frame_rate=audio_segment.frame_rate,
        sample_width=audio_segment.sample_width,
        channels=audio_segment.channels
    )

    normalized_audio.export(audio_path.parent / ("normalized_"+audio_path.name), format="mp3")
    return normalized_audio

if __name__ == "__main__":
    normalized_audio = normalize_volume(module_path/"static"/ "BONK.mp3")
    # AudioSegment.from_file(module_path/"static"/ "BONK.mp3")

