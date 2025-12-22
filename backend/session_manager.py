from typing import Optional, Tuple
import keyring
from dataclasses import dataclass

from backend.local_storage import LocalStorage


@dataclass
class User:
    username: str
    displayName: str
    pfp: str
    userid: str


class SessionManager:
    _instance = None

    currentSession: Optional[Tuple[str, User]] = None

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls.__new__(cls)
        return cls._instance

    def addSession(self, token: str, userdata: User):
        keyring.set_password("chatenium_uniend", userdata.userid, token)
        LocalStorage.instance().write(
            f"userdata_{userdata.userid}",
            userdata
        )

    def loadSessions(self):
        for file in LocalStorage.get_all():
            if file.startswith("userdata_"):
                self.currentSession = (
                    file.split("_", 1)[1],
                    LocalStorage.instance().read(file)
                )
