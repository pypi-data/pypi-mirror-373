from typing import Mapping, Dict
from json import dumps
from fastapi import Response, BackgroundTasks
from datetime import datetime
from tzlocal import get_localzone
from Osdental.ServicesBus.TaskQueue import task_queue
from Osdental.Shared.Enums.Constant import Constant

class CustomResponse(Response):

    def __init__(self, content: Dict[str,str] | str | None, status_code: int = 200, headers: Mapping[str, str] | None = None, media_type: str | None = None, background: BackgroundTasks | None = None, batch: str | None = None ):
        """ Custom Response constructor for FastAPI """
        self.content = content 
        self.local_tz = get_localzone()
        self.batch = batch

        # Use FastAPI Response constructor for standard attributes (status_code, media_type, etc.)
        super().__init__(
            content=content,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
        )

    async def send_to_service_bus(self) -> None:
        """ Send the response to the Service Bus asynchronously """
        id_message_log = self.headers.get('Idmessagelog') 
        message_json = {
            'idMessageLog': id_message_log,
            'type': 'RESPONSE',
            'dateExecution': datetime.now(self.local_tz).strftime('%Y-%m-%d %H:%M:%S'),
            'httpResponseCode': str(self.status_code),
            'messageOut': dumps(self.content) if isinstance(self.content, dict) else self.content,
            'batch': self.batch if self.batch else Constant.DEFAULT_EMPTY_VALUE,
            'errorProducer': Constant.DEFAULT_EMPTY_VALUE,
            'auditLog': Constant.MESSAGE_LOG_INTERNAL
        }
        await task_queue.enqueue(message_json)
