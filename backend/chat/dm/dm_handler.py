from typing import List

from backend.http import Http, HttpMethod, ResultType
from backend.session_manager import SessionManager
from dataclasses import dataclass, field
from backend.types import TimeStamp

@dataclass()
class Attachment:
    fileID: str
    fileName: str
    format: str
    type: str
    path: str
    height: int
    width: int
    hasThumbnail: bool

@dataclass()
class Message:
    msgid: str
    author: str
    message: str
    sent_at: TimeStamp
    isEdited: bool
    chatid: str
    seen: bool
    replyTo: str
    replyToId: str
    forwardedFrom: str
    forwardedFromName: str
    metaData: None = None
    files: List[Attachment] = field(default_factory=list)

class DmHandler(object):
    _instance = None

    # _listeners: List[Callable[[List[Chat]], None]] = []

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
        return cls._instance

    async def get_messages(self, chatid) -> List[Message]:
        print("Getting messages")

        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        result = await Http(
            HttpMethod.GET,
            f"chat/dm/messages?userid={SessionManager.instance().currentSession[1].userid}&chatid={chatid}&from={0}",
            None,
            Message,
        )

        if result.type == ResultType.SUCCESS:
            return result.success
        else:
            raise ValueError(result.error)