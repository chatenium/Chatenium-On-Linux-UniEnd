class Environments(object):
    _instance = None
    api_url = None
    ws_url = None
    cdn_url = None

    def __init__(self):
        raise RuntimeError("Call instance() instead")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print("Creating new Env instance")
            cls._instance = cls.__new__(cls)
            # Initialize instance variables
            cls._instance.api_url = "https://api.chatenium.hu"
            cls._instance.ws_url = "wss://api.chatenium.hu"
            cls._instance.ws_url = "https://cdn.chatenium.hu"
        return cls._instance

    def overwrite_env(self, api: str, ws: str, cdn: str):
        self.api_url = api
        self.ws_url = ws
        self.cdn_url = cdn
