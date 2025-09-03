import os
import mimetypes
from Osdental.Exception.ControlledException import ValidationDataException
from Osdental.Shared.Message import Message
from Osdental.Shared.Enums.FileType import FileType

class FileMetaData:
    def __init__(self, file_path: str):
        self.file_path = file_path
        self.name = ''
        self.ext = ''
        self.mime_type = 'application/octet-stream'
        self.type = 'other'
        self._extract_metadata()

    def _extract_metadata(self):
        if not self.file_path:
            raise ValidationDataException(error=Message.FILE_PATH_NOT_PROVIDED_MSG)

        self.name, ext = os.path.splitext(os.path.basename(self.file_path))
        self.ext = ext.lstrip('.')
        self.mime_type = mimetypes.guess_type(self.file_path)[0] or self.mime_type
        self.type = self._get_general_type(self.mime_type)

    def _get_general_type(self, mime_type: str) -> str:
        if mime_type.startswith('image/'):
            return FileType.IMAGE
        elif mime_type.startswith('video/'):
            return FileType.VIDEO
        elif mime_type.startswith('audio/'):
            return FileType.AUDIO
        elif mime_type in [
            'application/pdf',
            'application/msword',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            'text/plain'
        ]:
            return FileType.DOCUMENT
        elif mime_type in ['application/zip', 'application/x-rar-compressed']:
            return FileType.ARCHIVE
        else:
            return FileType.OTHER

    def to_dict(self):
        return {
            'name': self.name,
            'ext': self.ext,
            'type': self.type,
            'mimeType': self.mime_type
        }
