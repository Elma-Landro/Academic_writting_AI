import os
import json
import hashlib

class DiskCache:
    def __init__(self, cache_dir):
        self.cache_dir = cache_dir
        os.makedirs(cache_dir, exist_ok=True)

    def _hash(self, key):
        return hashlib.sha256(key.encode("utf-8")).hexdigest()

    def __contains__(self, key):
        path = os.path.join(self.cache_dir, self._hash(key) + ".json")
        return os.path.exists(path)

    def __getitem__(self, key):
        path = os.path.join(self.cache_dir, self._hash(key) + ".json")
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def __setitem__(self, key, value):
        path = os.path.join(self.cache_dir, self._hash(key) + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump(value, f, indent=2, ensure_ascii=False)
