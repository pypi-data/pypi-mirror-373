import re
import json
from datetime import datetime
from fastapi import Request
from tzlocal import get_localzone
from Osdental.ServicesBus.TaskQueue import task_queue
from Osdental.ExternalHttp.Client import APIClient
from Osdental.Models.Token import AuthToken
from Osdental.Encryptor.Jwt import JWT
from Osdental.Handlers.Instances import environment, microservice_name, microservice_version, aes, jwt_user_key
from Osdental.Handlers.DBSecurityQuery import DBSecurityQuery
from Osdental.Shared.Enums.Constant import Constant
from Osdental.Shared.Logger import logger
class CustomRequest:

    def __init__(self, request: Request):
        self.request = request
        self.local_tz = get_localzone()
        self.client = APIClient()

    async def send_to_service_bus(self) -> None:
        legacy = await DBSecurityQuery.get_legacy_data()
        message_in = await self.request.json()  
        request_data = Constant.DEFAULT_EMPTY_VALUE  
        match = re.search(r'data:\s*"([^"]+)"', message_in.get('query', ''))
        if match:
            encrypted_data = match.group(1)
            request_data = aes.decrypt(legacy.aes_key_user, encrypted_data)

        x_forwarded_for = self.request.headers.get('X-Forwarded-For')
        if x_forwarded_for:
            user_ip = x_forwarded_for.split(',')[0]
        else:
            user_ip = self.request.client.host

        if user_ip:
            location = await self.__get_location(user_ip)

        message_json = {
            'idMessageLog': self.request.headers.get('Idmessagelog'),
            'type': Constant.RESPONSE_TYPE_REQUEST,
            'environment': environment,
            'dateExecution': datetime.now(self.local_tz).strftime('%Y-%m-%d %H:%M:%S'),
            'header': json.dumps(dict(self.request.headers)),
            'microServiceUrl': str(self.request.url),
            'microServiceName': microservice_name,
            'microServiceVersion': microservice_version,
            'serviceName': message_in.get('operationName'),
            'machineNameUser': self.request.headers.get('Machinenameuser', Constant.DEFAULT_EMPTY_VALUE),
            'ipUser': user_ip or Constant.DEFAULT_EMPTY_VALUE,
            'userName': self.request.headers.get('Username', Constant.DEFAULT_EMPTY_VALUE),
            'localitation': location or Constant.DEFAULT_EMPTY_VALUE,
            'httpMethod': self.request.method,
            'httpResponseCode': Constant.DEFAULT_EMPTY_VALUE,
            'messageIn': request_data,
            'messageOut': Constant.DEFAULT_EMPTY_VALUE,
            'errorProducer': Constant.DEFAULT_EMPTY_VALUE,
            'auditLog': Constant.MESSAGE_LOG_INTERNAL,
            'batch': Constant.DEFAULT_EMPTY_VALUE,
            'idUser': self.__get_user_id(legacy.aes_key_user)
        }
        await task_queue.enqueue(message_json)

    async def __get_location(self, ip: str) -> str:
        try:
            response = await self.client.get(f'https://ipapi.co/{ip}/json/')
            if response.status_code == 200:
                data = response.json()
                return json.dumps({
                    'ip': ip,
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country_name'),
                    'latitude': data.get('latitude'),
                    'longitude': data.get('longitude'),
                })
            else:
                return Constant.DEFAULT_EMPTY_VALUE
        except Exception as e:
            logger.error(f'Error fetching location for IP {ip}: {e}')
            return Constant.DEFAULT_EMPTY_VALUE

    def __get_user_id(self, aes_key_user: str) -> str:
        authorization = self.request.headers.get('Authorization')
        user_token = None
        user_token_encrypted = None
        if authorization and authorization.startswith('Bearer '):
            user_token_encrypted = authorization.split(' ')[1]

        if user_token_encrypted:
            user_token = aes.decrypt(aes_key_user, user_token_encrypted)
            payload = JWT.extract_payload(user_token, jwt_user_key)
            token = AuthToken.from_jwt(payload)
            return token.id_user
        else:
            return Constant.DEFAULT_EMPTY_VALUE