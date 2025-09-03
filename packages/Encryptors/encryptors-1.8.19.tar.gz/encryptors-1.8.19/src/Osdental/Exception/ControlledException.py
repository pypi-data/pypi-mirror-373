from typing import Mapping
from datetime import datetime
from tzlocal import get_localzone
from Osdental.ServicesBus.TaskQueue import task_queue
from Osdental.Models.Response import Response
from Osdental.Shared.Enums.Code import Code
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Enums.Constant import Constant

class OSDException(Exception):
    """ Base class for all custom exceptions. """
    def __init__(self, message:str = Message.UNEXPECTED_ERROR_MSG, error:str=None, status_code:str = Code.APP_ERROR_CODE, headers:Mapping[str,str] | None = None):
        super().__init__(message)
        self.message = message
        self.error = error
        self.headers = headers
        self.status_code = status_code
        self.local_tz = get_localzone()

    async def send_to_service_bus(self) -> None:
        """ Method to send a message to the Service Bus. """
        if self.headers:
            message_json = {
                'idMessageLog': self.headers.get('Idmessagelog'),
                'type': Constant.RESPONSE_TYPE_ERROR,
                'dateExecution': datetime.now(self.local_tz).strftime('%Y-%m-%d %H:%M:%S'),
                'httpResponseCode': self.status_code,
                'messageOut': Constant.DEFAULT_EMPTY_VALUE,
                'errorProducer': self.error if self.error else Constant.DEFAULT_EMPTY_VALUE,
                'batch': Constant.DEFAULT_EMPTY_VALUE,
                'auditLog': Constant.MESSAGE_LOG_INTERNAL
            }
            await task_queue.enqueue(message_json)

    def get_response(self) -> Response:
        return Response(status=self.status_code, message=self.message).send()

    
class UnauthorizedException(OSDException):
    def __init__(
        self, 
        message:str = Message.PORTAL_ACCESS_RESTRICTED_MSG, 
        error:str = None, 
        status_code:str = Code.UNAUTHORIZATED_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class RequestDataException(OSDException):
    def __init__(
        self, 
        message:str = Message.INVALID_REQUEST_PARAMS_MSG, 
        error:str = None, 
        status_code:str = Code.INVALID_REQUEST_PARAMS_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class DatabaseException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.DATABASE_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class RSAEncryptException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.RSA_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class AESEncryptException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.AES_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class JWTokenException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.JWT_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class HttpClientException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.HTTP_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class AzureException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.AZURE_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class RedisException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.REDIS_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class ValidationDataException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.REQUEST_VALIDATION_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class UnexpectedException(OSDException):
    def __init__(
        self, 
        message:str = Message.UNEXPECTED_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.APP_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class MissingFieldException(OSDException):
    def __init__(
        self, 
        message:str = Message.MISSING_FIELD_ERROR_MSG, 
        error:str = None, 
        status_code:str = Code.MISSING_FIELD_ERROR_CODE, 
        headers:Mapping[str,str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class ProfilePermissionDeniedException(OSDException):
    def __init__(
        self,
        message: str = Message.PROFILE_PERMISSION_DENIED_MSG,
        error: str = None,
        status_code: str = Code.PROFILE_PERMISSION_DENIED_CODE,
        headers: Mapping[str, str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)

class InvalidFormatException(OSDException):
    def __init__(
        self,
        message: str = Message.INVALID_FORMAT_MSG,
        error: str = None,
        status_code: str = Code.INVALID_FORMAT_CODE,
        headers: Mapping[str, str] = None
    ):
        super().__init__(message=message, error=error, status_code=status_code, headers=headers)
