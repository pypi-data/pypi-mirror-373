from enum import StrEnum

class FileType(StrEnum):
    IMAGE = 'image'
    VIDEO = 'video'
    AUDIO = 'audio'
    DOCUMENT = 'document'
    ARCHIVE = 'archive'
    OTHER = 'other'