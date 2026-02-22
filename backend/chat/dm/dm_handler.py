import time
from pathlib import Path
from typing import List, Callable, Dict

from backend.http import Http, HttpMethod, ResultType
from backend.session_manager import SessionManager
from dataclasses import dataclass, field, asdict
from backend.types import TimeStamp
from backend.websocket import WebSocket
from backend.chat.file_uploader import FileUploader

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

@dataclass()
class FinishMessageReq:
    uploadId: str
    message: str
    username: str
    pfp: str
    replyTo: str
    replyToMessage: str
    chatid: str
    userid: str

@dataclass()
class JoinChatReq:
    userid: str
    connId: str
    chatid: str

@dataclass()
class EditMessageReq:
    messageId: str
    message: str
    chatid: str
    userid: str

@dataclass()
class DeleteMessageReq:
    messageId: str
    userid: str
    chatid: str

@dataclass
class WSMessageEditPayload:
    messageId: str
    message: str

@dataclass
class WSMessageRemovePayload:
    messageId: str

@dataclass
class ForwardMessageReq:
    messageId: str
    forwardTo: str
    chatid: str
    userid: str
    networkId: str
    forwardType: str

class DmHandler(object):
    _instance = None
    _listeners = {
        "add": [], # [Message]
        "edit": [], # WSMessageEditPayload
        "rem": [] # str
    }

    def __init__(self):
        raise RuntimeError('Call instance() instead')

    # Backend -> Frontend comms
    @classmethod
    def subscribe(cls, handler, channel: str):
        cls._listeners[channel].append(handler)

    @classmethod
    def unsubscribe(cls, handler, channel):
        cls._listeners[channel].remove(handler)

    @classmethod
    def _notify(cls, data, channel):
        print(f"Sending data to channel: {channel} with data: {data}")
        for listener in cls._listeners[channel]:
            listener(data)
    # Backend -> Frontend comms end

    # WS -> Backend -> Frontend
    @staticmethod
    @WebSocket.on("newMessage", Message)
    def _on_new_message(message: Message):
        cls = DmHandler
        cls._notify(message, "add")

    @staticmethod
    @WebSocket.on("editedMessage", WSMessageEditPayload)
    def _on_edited_message(payload: WSMessageEditPayload):
        cls = DmHandler
        cls._notify(payload, "edit")

    @staticmethod
    @WebSocket.on("deletedMessage", WSMessageRemovePayload)
    def _on_deleted_message(payload: WSMessageRemovePayload):
        cls = DmHandler
        cls._notify(payload.messageId, "rem")

    @classmethod
    def instance(cls):
        if cls._instance is None:
            print('Creating new instance')
            cls._instance = cls.__new__(cls)
        return cls._instance

    @classmethod
    async def get_messages(cls, chatid) -> List[Message]:
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

    @classmethod
    async def edit_message(cls, chatid: str, messageId: str, newMessage: str):
        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        result = await Http(
            HttpMethod.PATCH,
            "chat/dm/editMessage",
            asdict(EditMessageReq(
                messageId=messageId,
                message=newMessage,
                chatid=chatid,
                userid=SessionManager.instance().currentSession[1].userid,
            ))
        )

        if result.type == ResultType.SUCCESS:
            cls._notify(WSMessageEditPayload(
                messageId=messageId,
                message=newMessage
            ), "edit")
        else:
            raise ValueError(result.error.error)

    @classmethod
    async def delete_message(cls, chatid: str, messageId: str):
        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        result = await Http(
            HttpMethod.PATCH,
            "chat/dm/deleteMessage",
            asdict(DeleteMessageReq(
                userid=SessionManager.instance().currentSession[1].userid,
                messageId=messageId,
                chatid=chatid
            ))
        )

        if result.type == ResultType.SUCCESS:
            cls._notify(messageId, "rem")
        else:
            raise ValueError(result.error.error)

    @classmethod
    async def send_message(cls, chatid: str, message: str, reply_to: str, reply_to_message: str, files: List[Path] = []):
        print("Sending message")
        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        upload_id = ""
        if files:
            print("Files provided, calling file uploader...")
            uploader = FileUploader()
            try:
                upload_id = await uploader.upload_files(files, chatid)
                print("File uploader signaled success")
            except Exception as e:
                print("File uploader signaled error")
                raise e

        result = await Http(
            HttpMethod.POST,
            "chat/dm/finishMessage",
            asdict(FinishMessageReq(
                message=message,
                username=SessionManager.instance().currentSession[1].username,
                replyToMessage=reply_to_message,
                chatid=chatid,
                replyTo=reply_to,
                uploadId=upload_id,
                pfp=SessionManager.instance().currentSession[1].pfp,
                userid=SessionManager.instance().currentSession[1].userid,
            )),
            Message
        )

        if result.type == ResultType.SUCCESS:
            cls._notify(result.success, "add")
        else:
            raise ValueError(result.error)

    @classmethod
    async def join_chat(cls, chatid: str):
        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        if WebSocket.instance().connectionId is None:
            time.sleep(1)
            await cls.join_chat(chatid)
            return

        result = await Http(
            HttpMethod.POST,
            "v2/chat/dm/joinWebSocketRoom",
            asdict(JoinChatReq(
                chatid=chatid,
                userid=SessionManager.instance().currentSession[1].userid,
                connId=WebSocket.instance().connectionId,
            ))
        )

        if result.type == ResultType.SUCCESS:
            print(f"Joined chat successfully as {WebSocket.instance().connectionId}")
        else:
            raise ValueError(result.error)

    @classmethod
    async def forward_chat(cls, messageId: str, forwardTo: str, chatid: str):
        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        result = await Http(
            HttpMethod.POST,
            "chat/dm/forwardMessage",
            asdict(ForwardMessageReq(
                messageId=messageId,
                forwardTo=forwardTo,
                chatid=chatid,
                userid=SessionManager.instance().currentSession[1].userid,
                networkId="",
                forwardType="dm",
            )),
            Message,
        )

        if result.type == ResultType.SUCCESS:
            print(f"Forwarded message successfully")
        else:
            raise ValueError(result.error)