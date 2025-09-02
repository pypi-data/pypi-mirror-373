import json
import os
import time
import portalocker
from datetime import datetime, timedelta

class FileTokenManager:
    def __init__(self, filepath: str):
        self.filepath = filepath
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)

    def _read_token(self):
        if not os.path.exists(self.filepath):
            return None
        with portalocker.Lock(self.filepath, 'r', timeout=2) as f:
            return json.load(f)

    def _write_token(self, token_data):
        with portalocker.Lock(self.filepath, 'w', timeout=2) as f:
            json.dump(token_data, f)

    def set_token(self, access_token, refresh_token, expires_in: int = 3600):
        expiry_time = (datetime.utcnow() + timedelta(seconds=expires_in)).isoformat()
        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expiry_time
        }
        self._write_token(token_data)

    def get_token(self):
        token_data = self._read_token()
        return token_data.get("access_token") if token_data else None

    def is_token_valid(self):
        token_data = self._read_token()
        if not token_data or "expires_at" not in token_data:
            return False
        return datetime.fromisoformat(token_data["expires_at"]) > datetime.utcnow()

    def clear_token(self):
        if os.path.exists(self.filepath):
            try:
                os.remove(self.filepath)
            except Exception as e:
                print(f"Warning: Could not delete token file: {e}")

    def refresh_token_with_lock(self, refresh_func):
        """Centralized refresh logic. Only one process will refresh; others will wait."""
        lockfile = self.filepath + ".lock"
        with portalocker.Lock(lockfile, timeout=60):
            # Check again inside lock in case another process already refreshed
            if self.is_token_valid():
                return
            # Refresh token using the passed-in callback (ABRestProcessor)
            access_token, refresh_token, expires_in = refresh_func()
            self.set_token(access_token, refresh_token, expires_in)

    def ensure_token_ready(self, refresh_callback=None):
        """Ensure that a valid token is available. Only one process refreshes it."""
        if self.is_token_valid():
            return

        lock_file = self.filepath + ".lock"

        # Lock ensures only one process can refresh
        with portalocker.Lock(lock_file, timeout=30):
            if not self.is_token_valid():
                print("[TokenManager] Token is invalid. Refreshing...")
                if refresh_callback:
                    refresh_callback()
            else:
                print("[TokenManager] Another process already refreshed the token.")

