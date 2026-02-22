from typing import Optional, Tuple
import keyring
from dataclasses import dataclass, asdict

from backend.local_storage import LocalStorage

@dataclass()
class User:
    username: str
    displayName: str
    pfp: str
    userid: str

@dataclass()
class LogoutReq:
    token: str
    userid: str

class SessionManager(object):
    _instance = None

    currentSession: Optional[Tuple[str, User]] = None

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

    def loadSessions(self) -> bool:
        for file in LocalStorage.get_all():
            if file.startswith("userdata_"):
                token = keyring.get_password("chatenium_uniend", file.split("_")[1])
                self.currentSession = (token, User(**LocalStorage.instance().read(file)))
                return True

        return False

    async def logout(self):
        from backend.http import Http, HttpMethod, ResultType

        if not SessionManager.instance().currentSession:
            raise ValueError("No session")

        result = await Http(
            method=HttpMethod.POST,
            path="user/logout",
            data=asdict(LogoutReq(
                token=SessionManager.instance().currentSession[0],
                userid=SessionManager.instance().currentSession[1].userid
            ))
        )

        if result.type == ResultType.SUCCESS:
            LocalStorage.instance().delete(f"userdata_{SessionManager.instance().currentSession[1].userid}")
            self.currentSession = None
            print("Logout successful")
        else:
            raise ValueError(result.error)