import os

class Environments(object):
    api_url = os.environ.get("API_URL", "https://api.chatenium.hu")
    ws_url = os.environ.get("WS_URL", "wss://api.chatenium.hu")

    def overwrite_env(self, api: str, ws: str):
        self.api_url = api
        self.ws_url = ws