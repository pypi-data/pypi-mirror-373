import requests
import json
import os

class ItryID:

    def __init__(self, server_url: str, game_name: str, local_save: str = "progress.json"):
        self.server_url = server_url
        self.game_name = game_name
        self.local_save = local_save
        self.user = {"user_id": None, "username": "Guest"}

        self.load_local()
    def load_local(self):
        if os.path.exists(self.local_save):
            try:
                with open(self.local_save, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    self.user.update(data)
            except Exception:
                pass

    def save_local(self):
        with open(self.local_save, "w", encoding="utf-8") as f:
            json.dump(self.user, f, ensure_ascii=False, indent=2)

    def _api_post(self, payload: dict) -> dict:
        try:
            r = requests.post(self.server_url, data=payload, timeout=8)
            return r.json()
        except Exception as e:
            return {"status": "network_error", "error": str(e)}

    def register(self, username: str, password: str) -> dict:
        return self._api_post({"action":"register", "username": username, "password": password})

    def login(self, username: str, password: str) -> dict:
        res = self._api_post({"action":"login", "username": username, "password": password})
        if res.get("status") == "success":
            self.user["user_id"] = res.get("user_id")
            self.user["username"] = username
        return res

    def join_game(self) -> dict:
        if not self.user["user_id"]:
            return {"status":"error", "msg":"user_not_logged_in"}
        return self._api_post({"action":"join_game", "user_id": self.user["user_id"], "game_name": self.game_name})

    def save_progress(self, progress: dict = None) -> dict:
        if progress:
            self.user.update(progress)
        if self.user["user_id"]:
            self.join_game()  # создаем запись user<->game
            res = self._api_post({
                "action": "save_progress",
                "user_id": self.user["user_id"],
                "game_name": self.game_name,
                "progress_json": json.dumps(self.user)
            })
            return res
        else:
            self.save_local()
            return {"status":"saved_locally"}

    def logout(self):
        self.user = {"user_id": None, "username": "Guest"}
        self.save_local()
