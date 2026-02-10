import base64
import json
import math
import mimetypes
import uuid
from dataclasses import dataclass, asdict, field
from pathlib import Path
from typing import List

from backend.http import Http, HttpMethod, ResultType
from backend.session_manager import SessionManager


@dataclass
class FileUploadRegistration:
    size: int
    type: str
    fileId: str
    name: str

@dataclass
class RegisterUploadReq:
    files: List[FileUploadRegistration]
    roomId: str
    userid: str

@dataclass
class RegisterUploadResp:
    uploadId: str

@dataclass
class UploadChunkReq:
    uploadId: str
    roomId: str
    fileId: str
    chunk: str
    userid: str

@dataclass
class FinishUploadReq:
    uploadId: str
    roomId: str
    userid: str

class FileUploader():
    def _calculate_chunk_size(self, file_size):
        MIN_CHUNK_SIZE = 25000000 # 25 MB
        chunks = math.floor(file_size / MIN_CHUNK_SIZE)
        if chunks == 0:
            return file_size
        chunkSize = math.ceil(file_size / chunks)
        return max(chunkSize, MIN_CHUNK_SIZE)

    def _fetch_mime_type(self, path: Path) -> str:
        mime_type, _ = mimetypes.guess_type(str(path))

        if mime_type is None:
            return "file"

        if mime_type.startswith("image/"):
            return "image"
        elif mime_type.startswith("video/"):
            return "video"
        elif mime_type.startswith("audio/"):
            return "audio"
        else:
            return "file"


    async def upload_files(self, attachments: List[Path], room_id: str) -> str:
        print(f"Starting new upload session at {room_id}... {attachments}")

        if SessionManager.instance().currentSession is None:
            raise ValueError("No session")

        registrations: List[FileUploadRegistration] = []

        for attachment in attachments:
            file_type = self._fetch_mime_type(attachment)
            file_id = str(uuid.uuid4())

            registrations.append(FileUploadRegistration(
                type=file_type,
                fileId=file_id,
                name=attachment.name,
                size=attachment.stat().st_size,
            ))

        result = await Http(
            method=HttpMethod.POST,
            path="chat/cdnRegisterUpload",
            data=asdict(RegisterUploadReq(
                files=registrations,
                roomId=room_id,
                userid=SessionManager.instance().currentSession[1].userid,
            )),
            successType=RegisterUploadResp
        )

        if result.type == ResultType.SUCCESS:
            print("Upload registration successful. Upload files...")

            for attachment, reg in zip(attachments, registrations):
                try:
                    await self._upload_file(attachment, reg, room_id, result.success.uploadId)
                except Exception as e:
                    raise e

            print("All files uploaded successfully. Finishing upload...")

            fresult = await Http(
                method=HttpMethod.POST,
                path="chat/finishUpload",
                data=asdict(FinishUploadReq(
                    uploadId=result.success.uploadId,
                    roomId=room_id,
                    userid=SessionManager.instance().currentSession[1].userid,
                )),
                cdn_req=True,
            )

            if fresult.type == ResultType.SUCCESS:
                print("File upload session finished successfully.")
                return result.success.uploadId
            else:
                print("File upload finalization failed")
                raise ValueError("File upload finalization failed")
        else:
            print("Upload registration failed.")
            raise ValueError(result.error)

    async def _upload_file(self, file: Path, registration: FileUploadRegistration, room_id: str, upload_id: str):
        print(f"Uploading file {registration.name}")
        chunk_size = self._calculate_chunk_size(registration.size)

        with open(file, "rb") as f:
            while True:
                chunk = f.read(chunk_size)
                if not chunk: # EOF
                    break

                try:
                    await self._upload_chunk(room_id, base64.b64encode(chunk).decode("utf-8"), upload_id, registration.fileId)
                except Exception as e:
                    raise e

    async def _upload_chunk(self, room_id: str, chunk: str, upload_id: str, file_id: str):
        result = await Http(
            method=HttpMethod.POST,
            path="chat/uploadChunk",
            data=asdict(UploadChunkReq(
                uploadId=upload_id,
                roomId=room_id,
                fileId=file_id,
                chunk=chunk,
                userid=SessionManager.instance().currentSession[1].userid,
            )),
            cdn_req=True
        )

        if result.type == ResultType.SUCCESS:
            print("Chunk upload success.")
            return
        else:
            print("CHUNK UPLOAD FAILED.")
            raise ValueError("Chatenium CDN has returned an error on chunk upload")