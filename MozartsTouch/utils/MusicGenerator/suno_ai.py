from pathlib import Path
import time
import requests
from loguru import logger
import yaml

module_path = Path(__file__).resolve().parent.parent.parent # module_path为模块根目录（`/MozartsTouch`）
with open(module_path / 'config.yaml', 'r', encoding='utf8') as file:
    config = yaml.safe_load(file)

class Suno:
    def __init__(self) -> None:
        self.base_url = config['MUSIC_MODEL_CONFIG']['API_BASE_URL']
        self.task_list = {
            'custom_generate_audio': f"{self.base_url}/api/custom_generate",
            'extend_audio': f"{self.base_url}/api/extend_audio",
            'generate_audio_by_prompt': f"{self.base_url}/api/generate",
            'get_audio_information': f"{self.base_url}/api/get?ids=",
            'get_quota_information': f"{self.base_url}/api/get_limit"
        }

    def post_suno_api(self, task, payload):
        url = self.task_list[task]
        response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
        response.raise_for_status()
        return response.json()
    
    def get_suno_api(self, task, audio_ids=None):
        url = self.task_list[task]
        if audio_ids:
            url += audio_ids

        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def generate(self, text: str):
        data = self.post_suno_api('generate_audio_by_prompt', {
            "prompt": text,
            "make_instrumental": True,
            "wait_audio": False
        })
        ids = ",".join([item['id'] for item in data])
        logger.info(f"Generated IDs: {ids}")

        for _ in range(60):
            try:
                data = self.get_suno_api('get_audio_information', ids)
                if data[1]["status"] == 'streaming':
                    logger.info(f"Audio URL: {data[1]['audio_url']}")
                    return data[1]['audio_url']
            except Exception as e:
                logger.warning(f"Error fetching audio information: {e}")
            time.sleep(5)

        logger.error("Failed to generate audio within the expected time.")
        return None

if __name__ == '__main__':
    suno = Suno()
    music = suno.generate("A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously.")
    print(music)