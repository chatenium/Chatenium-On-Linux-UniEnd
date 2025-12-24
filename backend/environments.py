import os

class Environments(object):
    _instance = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new Env instance')
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
        return cls._instance
    
    api_url = os.environ.get("API_URL", "https://api.chatenium.hu")
    ws_url = os.environ.get("WS_URL", "wss://api.chatenium.hu")

    def overwrite_env(self, api: str, ws: str):
        self.api_url = api
        self.ws_url = ws
