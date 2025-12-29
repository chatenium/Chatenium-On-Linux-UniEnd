from typing import List, Callable, Optional

from backend.http import Http, HttpMethod, ResultType
from backend.session_manager import SessionManager
from dataclasses import dataclass, asdict


@dataclass()
class Chat:
    userid: str
    chatid: str
    username: str
    displayName: str
    pfp: str
    status: int
    pinnedMessages: str
    type: str
    muted: bool
    notifications: Optional[int] = 0

@dataclass()
class StartNewChatReq:
    userid: str
    peerUsername: str

class ChatsHandler(object):
    _instance = None
    _listeners: List[Callable[[List[Chat]], None]] = []
    _chats: List[Chat] = []

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    def subscribe(cls, listener: Callable[[Chat], None]):
        cls._listeners.append(listener)

    @classmethod
    def unsubscribe(cls, listener: Callable[[Chat], None]):
        cls._listeners.remove(listener)

    @classmethod
    def _notify(cls, chats: List[Chat]):
        for fn in cls._listeners:
            fn(chats)

    @classmethod
    async def startNew(cls, peerUsername: str):
        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        result = await Http(
            HttpMethod.POST,
            "chat/startNew",
            asdict(StartNewChatReq(userid=SessionManager.instance().currentSession[1].userid, peerUsername=peerUsername)),
            Chat,
        )

        if result.type == ResultType.SUCCESS:
            cls._chats.append(result.success)
            cls._notify(cls._chats)
        else:
            raise ValueError(result.error)

    @classmethod
    async def getChats(cls) -> List[Chat]:
        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        result = await Http(
            HttpMethod.GET,
            f"chat/get?userid={SessionManager.instance().currentSession[1].userid}",
            None,
            Chat,
        )

        if result.type == ResultType.SUCCESS:
            cls._notify(result.success)
            cls._chats = result.success
            return result.success
        else:
            raise ValueError(result.error)
