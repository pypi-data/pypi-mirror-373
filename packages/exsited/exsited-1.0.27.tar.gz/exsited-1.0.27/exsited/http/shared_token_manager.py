# shared_token_manager.py
from multiprocessing import Manager, Lock
from datetime import datetime, timedelta

class SharedTokenManager:
    def __init__(self, manager_dict, lock):
        self.store = manager_dict
        self.lock = lock

    def is_token_valid(self):
        with self.lock:
            token = self.store.get("token")
            expiry = self.store.get("expiry")
            if not token or not expiry:
                return False
            return datetime.utcnow() < expiry

    def get_token(self):
        with self.lock:
            return self.store.get("token")

    def set_token(self, token: str, expires_in: int):
        with self.lock:
            self.store["token"] = token
            self.store["expiry"] = datetime.utcnow() + timedelta(seconds=expires_in)

    def clear_token(self):
        with self.lock:
            self.store.clear()
