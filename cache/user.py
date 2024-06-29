import json

class UserCache:
    _instance = None
    _cache = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(UserCache, cls).__new__(cls)
        return cls._instance

    @property
    def cache(self):
        return self._cache

    def update_user(self, user):
        self._cache[user.user_id] = user
