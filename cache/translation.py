import json

class TranslationCache:
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TranslationCache, cls).__new__(cls)
            cls._instance.load_translations()
        return cls._instance

    @property
    def cache(self):
        return self._cache

    def load_translations(self):
        with open('texts.json', 'r', encoding='utf-8') as f:
            self._cache = json.load(f)

    def reload_translations(self):
        self.load_translations()