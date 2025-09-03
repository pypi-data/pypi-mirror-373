import json
from base64 import b64decode, b64encode
from typing import Dict
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from Osdental.Exception.ControlledException import RSAEncryptException
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Enums.Constant import Constant

class RSAEncryptor:

    @staticmethod
    def encrypt(data:str | Dict[str,str], public_key_rsa:str) -> str:
        try:
            if isinstance(data, dict):
                data = json.dumps(data)

            public_key = serialization.load_pem_public_key(public_key_rsa.encode(Constant.DEFAULT_ENCODING))
            data_bytes = data.encode(Constant.DEFAULT_ENCODING)
            encrypted_bytes = public_key.encrypt(
                data_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            return b64encode(encrypted_bytes).decode(Constant.DEFAULT_ENCODING)

        except Exception as e:
            logger.error(f'Unexpected RSA encryption error: {str(e)}')
            raise RSAEncryptException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e)) 


    @staticmethod
    def decrypt(data:str, private_key_rsa:str, silent:bool = False) -> str:
        try:
            encrypted_bytes = b64decode(data)
            private_key = serialization.load_pem_private_key(private_key_rsa.encode(Constant.DEFAULT_ENCODING), password=None)
            decrypted_bytes = private_key.decrypt(
                encrypted_bytes,
                padding.OAEP(
                    mgf=padding.MGF1(algorithm=hashes.SHA256()),
                    algorithm=hashes.SHA256(),
                    label=None
                )
            )

            return decrypted_bytes.decode(Constant.DEFAULT_ENCODING)

        except Exception as e:
            if not silent:
                logger.error(f'Unexpected RSA decryption error: {str(e)}')
                
            raise RSAEncryptException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))