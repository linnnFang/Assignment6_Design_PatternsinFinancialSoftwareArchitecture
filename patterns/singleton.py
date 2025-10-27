# singleton.py
import json

class Config:
    _instance = None

    def __new__(cls, path="config.json"):
        if cls._instance is None:
            print(f"[Config] Loading from {path}")
            cls._instance = super().__new__(cls)
            cls._instance._load(path)
        else:
            print("[Config] Reusing existing instance")
        return cls._instance

    def _load(self, path):
        with open(path, "r", encoding="utf-8") as f:
            self._data = json.load(f)

    def get(self, key, default=None):
        return self._data.get(key, default)





