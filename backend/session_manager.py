from typing import Optional
import keyring
from dataclasses import dataclass, asdict

from backend.local_storage import LocalStorage

class SessionManager(object):
    _instance = None

    currentSession: Optional[str, User] = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
            # Put any initialization here.
        return cls._instance

    def addSession(self, token: str, userdata: User):
        print(token, userdata)
        keyring.set_password("chatenium_uniend", userdata.userid, token)
        LocalStorage.instance().write(f"userdata_{userdata.userid}", userdata)

    def loadSessions(self):
        for file in LocalStorage.get_all():
            print(file)
            if file.startswith("userdata_"):
                self.currentSession = (file.split("_")[1], LocalStorage.instance().read(file))

    @dataclass()
    class User:
        username: str
        displayName: str
        pfp: str
        userid: str