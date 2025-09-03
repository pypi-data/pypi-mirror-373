import os
import json
import base64
from typing import Dict, List
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from Osdental.Exception.ControlledException import AESEncryptException
from Osdental.Shared.Logger import logger
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Enums.Constant import Constant

class AES:

    def __init__(self):
        self.IV_LENGTH = 32
        self.TAG_LENGTH = 16

    @staticmethod
    def generate_key() -> str:
        """Generates a random 256-bit AES key and returns it Base64 encoded."""
        key = os.urandom(32)
        return base64.b64encode(key).decode(Constant.DEFAULT_ENCODING)
    
    def encrypt(self, aes_key:str, data:Dict[str,str] | str | List[Dict[str,str]]) -> str:
        """
        Encrypts data using AES-GCM.
        Supports dictionary, string, or list inputs.

        :param aes_key: AES key in Base64 format.
        :param data: Data to be encrypted (dict, str, or list).
        :return: Data encrypted in Base64.
        """
        if not isinstance(data, (dict, str, list)):
            raise ValueError(AES_INPUT)

        try:
            key = base64.b64decode(aes_key)
            iv = os.urandom(self.IV_LENGTH)
            if isinstance(data, (dict, list)):
                json_data = json.dumps(data)
            else:
                json_data = data

            cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
            encryptor = cipher.encryptor()
            ciphertext = encryptor.update(json_data.encode(Constant.DEFAULT_ENCODING)) + encryptor.finalize()
            tag = encryptor.tag
            encrypted_data = iv + ciphertext + tag

            return base64.b64encode(encrypted_data).decode(Constant.DEFAULT_ENCODING)

        except Exception as e:
            logger.error(f'Unexpected AES encryption error: {str(e)}')
            raise AESEncryptException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))
 

    def decrypt(self, aes_key:str, encrypted_data:str, silent:bool = False):
        """
        Decrypts data using AES-GCM.
        Expects encrypted data to represent either a JSON object (dict) or a plain string.

        :param aes_key: AES key in Base64 format.
        :param encrypted_data: Data encrypted in Base64.
        :return: Decrypted data (either dict or str).
        """
        try:
            key = base64.b64decode(aes_key)
            encrypted_data = base64.b64decode(encrypted_data)
            iv = encrypted_data[:self.IV_LENGTH]
            tag = encrypted_data[-self.TAG_LENGTH:]
            ciphertext = encrypted_data[self.IV_LENGTH:-self.TAG_LENGTH]
            cipher = Cipher(algorithms.AES(key), modes.GCM(iv, tag))
            decryptor = cipher.decryptor()
            plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            try:
                decrypted_data = json.loads(plaintext.decode(Constant.DEFAULT_ENCODING))
                return decrypted_data
            except json.JSONDecodeError:
                return plaintext.decode(Constant.DEFAULT_ENCODING)

        except Exception as e:
            if not silent:
                logger.error(f'Unexpected AES decryption error: {str(e)}')
                
            raise AESEncryptException(message=Message.UNEXPECTED_ERROR_MSG, error=str(e))