from dataclasses import dataclass, field, asdict
from enum import Enum
from Osdental.Shared.Enums.Code import Code
from Osdental.Shared.Enums.Message import Message

@dataclass
class Response:
    status: str = field(default=Code.PROCESS_SUCCESS_CODE)
    message: str = field(default=Message.PROCESS_SUCCESS_MSG)
    data: str = field(default=None)

    def __post_init__(self):
        # Asegura que status y message sean str si son Enum
        if isinstance(self.status, Enum):
            self.status = str(self.status)
        if isinstance(self.message, Enum):
            self.message = str(self.message)

    def send(self):
        return asdict(self)
