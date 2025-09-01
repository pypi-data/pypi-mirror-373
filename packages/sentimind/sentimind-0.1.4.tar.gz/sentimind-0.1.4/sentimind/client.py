# sentimind/client.py
import requests

class SentimindClient:
    def __init__(self, base_url: str = "https://sentimind-labs.com"):
        self.base_url = base_url.rstrip("/")

    def health(self):
        resp = requests.get(f"{self.base_url}/v1/health")
        resp.raise_for_status()
        return resp.json()

    def analyze_single(self, text: str):
        payload = {"text": text}
        resp = requests.post(f"{self.base_url}/v1/analyze/sentiment/single", json=payload)
        resp.raise_for_status()
        return resp.json()

    def analyze_batch(self, texts: list[str]):
        payload = {"texts": texts}
        resp = requests.post(f"{self.base_url}/v1/analyze/sentiment/batch", json=payload)
        resp.raise_for_status()
        return resp.json()
