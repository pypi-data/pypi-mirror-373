from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from typing import Dict
import jwt
from datetime import datetime, timezone, timedelta
from Osdental.Handlers.DBCatalogQuery import DBCatalogQuery
from Osdental.Handlers.DBConnection import DBConnection
from Osdental.Shared.Enums.Message import Message
from Osdental.Exception.ControlledException import MissingFieldException

class CData:
    @staticmethod
    async def generate_token_initial():    
        return await CData.__generate_jwt()

    @staticmethod
    async def generate_token_account(sub_account: str = None):    
        return await CData.__generate_jwt(sub_account)

    @staticmethod
    async def __generate_jwt(sub_account: str = None) -> Dict[str, str]:        
        if sub_account is None or sub_account != '':                        
            now = datetime.now(timezone.utc)            
            iat = int(now.timestamp())                        
            catalog = await DBCatalogQuery.get_catalog_data('CDataIntegration')     
            data_credentials = await DBConnection.get_data_credentials('CData')                                     

            if catalog and data_credentials:
                exp = int((now + timedelta(minutes=data_credentials.get('expToken'))).timestamp())            
                        
                payload = {
                    'tokenType': catalog.get('tokenType'),
                    'iss': catalog.get('ISS'),
                    'iat': iat,
                    'exp': exp
                }            
                if sub_account:
                    payload['sub'] = sub_account
                private_key = CData.generate_private_key(data_credentials.get('keyPrivate'))            
                token = jwt.encode(payload, private_key, algorithm='RS256')                                                                    
                return token
            else:
                raise MissingFieldException(message=Message.CATALOG_DATA_CREDENTIALS_MISSED)
        else:             
            raise MissingFieldException(message=Message.SUB_ACCOUNT_REQUIRED)

    @staticmethod
    def generate_private_key(private_rsa: str):                  
        private_key = serialization.load_pem_private_key(
            private_rsa.encode(),
            password=None,
            backend=default_backend()
        )
        return private_key    