import time
import requests
from io import BytesIO
base_url = 'http://localhost:3000/'


def custom_generate_audio(payload):
    url = f"{base_url}/api/custom_generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def extend_audio(payload):
    url = f"{base_url}/api/extend_audio"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()

def generate_audio_by_prompt(payload):
    url = f"{base_url}/api/generate"
    response = requests.post(url, json=payload, headers={'Content-Type': 'application/json'})
    return response.json()


def get_audio_information(audio_ids):
    url = f"{base_url}/api/get?ids={audio_ids}"
    response = requests.get(url)
    return response.json()


def get_quota_information():
    url = f"{base_url}/api/get_limit"
    response = requests.get(url)
    return response.json()

class Suno:
    @classmethod
    def generate(self, text: str):
        data = generate_audio_by_prompt({
            "prompt": text,
            "make_instrumental": True,
            "wait_audio": False
        })
        # print(data)
        ids = f"{data[0]['id']},{data[1]['id']}"
        print(f"ids: {ids}")

        for _ in range(60):
            try:
                data = get_audio_information(ids)
                if data[1]["status"] == 'streaming':
                    print(f"{data[1]['id']} ==> {data[1]['audio_url']}")
                    return data[1]['audio_url']
            except: continue
            # sleep 5s
            time.sleep(5)


if __name__ == '__main__':
    data = generate_audio_by_prompt({
        "prompt": "A popular heavy metal song about war, sung by a deep-voiced male singer, slowly and melodiously. The lyrics depict the sorrow of people after the war.",
        "make_instrumental": False,
        "wait_audio": False
    })
    print(data)
    ids = f"{data[0]['id']},{data[1]['id']}"
    print(f"ids: {ids}")

    for _ in range(60):
        data = get_audio_information(ids)
        if data[0]["status"] == 'streaming':
            print(f"{data[0]['id']} ==> {data[0]['audio_url']}")
            print(f"{data[1]['id']} ==> {data[1]['audio_url']}")
            break
        # sleep 5s
        time.sleep(5)