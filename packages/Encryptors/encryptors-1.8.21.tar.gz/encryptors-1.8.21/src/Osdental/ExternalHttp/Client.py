import os
import json
import asyncio
import httpx
from datetime import datetime
from typing import Dict
from dotenv import load_dotenv
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type
from Osdental.ServicesBus.TaskQueue import task_queue
from Osdental.Exception.ControlledException import HttpClientException
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Enums.Constant import Constant

load_dotenv(dotenv_path='.env', override=True)

class APIClient(httpx.AsyncClient):

    def __init__(self, **kwargs):
        timeout = kwargs.pop('timeout', httpx.Timeout(10.0, read=20.0))
        super().__init__(follow_redirects=True, timeout=timeout, **kwargs)

    @retry(
        retry=retry_if_exception_type(httpx.RequestError),
        stop=stop_after_attempt(3),  
        wait=wait_exponential(multiplier=1, min=2, max=10),  
        reraise=True
    )
    async def _perform_request(self, method: str, url: str, *args, **kwargs):
        response = await self.request(method, url, *args, **kwargs)
        response.raise_for_status()
        return response
    
    async def rest_request(self, method:str, url:str, *args, **kwargs) -> str:
        try:
            headers = kwargs.get('headers', {})
            asyncio.create_task(self.send_request_to_service_bus(endpoint=url, body=kwargs.get('body'), headers=headers))
            response = await self._perform_request(method, url, *args, **kwargs)    
            asyncio.create_task(self.send_response_to_service_bus(response, headers=headers))
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                return response.json()
            elif 'text/' in content_type or 'html' in content_type or 'xml' in content_type:
                return response.text
            else:
                return response.content
        
        except httpx.RequestError as e:
            logger.error(f'Unexpected rest request error: {str(e)}')
            raise HttpClientException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))


    @retry(
        retry=retry_if_exception_type(httpx.RequestError),
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def _perform_graphql_request(self, url: str, consult: str, variables: Dict[str, str], headers: dict):
        response = await self.post(url, json={'query': consult, 'variables': variables}, headers=headers)
        response.raise_for_status()
        return response
    
    async def graphql_request(self, url:str, consult:str, variables:Dict[str,str], **kwargs) -> str:
        try:
            headers = kwargs.get('headers', {})
            asyncio.create_task(self.send_request_to_service_bus(endpoint=url, body=variables, headers=headers))
            response = await self._perform_graphql_request(url, consult, variables, headers)
            asyncio.create_task(self.send_response_to_service_bus(response, headers=headers))
            content_type = response.headers.get('content-type', '').lower()
            if 'application/json' in content_type:
                return response.json()
            elif 'text/' in content_type or 'html' in content_type or 'xml' in content_type:
                return response.text
            else:
                return response.content
        
        except httpx.RequestError as e:
            logger.error(f'Unexpected grahql request error: {str(e)}')
            raise HttpClientException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))
        

    async def send_request_to_service_bus(self, endpoint:str, body:Dict[str,str], headers:Dict[str,str]) -> None:
        """
        Send a message to the Service Bus with details about the request made:

        :param endpoint: (str): URL of the endpoint to which the request will be made.
        :param body: (Dict[str, Any]): Body of the request (usually in JSON format).
        """
        message_json = {
            'idMessageLog': headers.get('Idmessagelog'),
            'type': 'REQUEST',
            'environment': os.getenv('ENVIRONMENT'),
            'dateExecution': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'header': json.dumps(dict(headers)),
            'microServiceUrl': endpoint,
            'microServiceName': os.getenv('MICROSERVICE_NAME'),
            'microServiceVersion': os.getenv('MICROSERVICE_VERSION'),
            'serviceName': body.get('operationName') if body else '*',
            'machineNameUser': headers.get('Machinenameuser'),
            'ipUser': headers.get('Ipuser'),
            'userName': headers.get('Username'),
            'localitation': headers.get('Localitation'),
            'httpMethod': 'POST',
            'httpResponseCode': '*',
            'messageIn': json.dumps(body) if body else '*',
            'messageOut': '*',
            'errorProducer': '*',
            'auditLog': Constant.MESSAGE_LOG_EXTERNAL
        }
        await task_queue.enqueue(message_json)

    async def send_response_to_service_bus(self, response:httpx.Response, headers:Dict[str,str]) -> None:
        """
        Send a message to the Service Bus with details about the response received:

        :param response: (Response): Response object received from the endpoint.
        """
        message_json = {
            'idMessageLog': headers.get('Idmessagelog'),
            'type': 'RESPONSE',
            'dateExecution': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'httpResponseCode': str(response.status_code),
            'messageOut': json.dumps(response.json()),
            'auditLog': Constant.MESSAGE_LOG_EXTERNAL
        }
        await task_queue.enqueue(message_json)