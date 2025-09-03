from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from Osdental.Shared.Utils.CaseConverter import CaseConverter
from Osdental.Exception.ControlledException import MissingFieldException
from Osdental.Shared.Enums.Message import Message

@dataclass
class Legacy:
    id_legacy: str
    legacy_name: str
    id_enterprise: str
    refresh_token_exp_min: int
    access_token_exp_min: int
    public_key2: str
    private_key1: str
    private_key2: str
    aes_key_user: str
    aes_key_auth: str

    def __post_init__(self):
        if not self.legacy_name:
            raise MissingFieldException(message=Message.LEGACY_NAME_REQUIRED_MSG)
        
        if not self.refresh_token_exp_min:
            raise MissingFieldException(message=Message.REFRESH_TOKEN_EXP_REQUIRED_MSG)
        
        if not self.access_token_exp_min:
            raise MissingFieldException(message=Message.ACCESS_TOKEN_EXP_REQUIRED_MSG)
        
        if not self.public_key2:
            raise MissingFieldException(message=Message.PUBLIC_KEY2_REQUIRED_MSG)
        
        if not self.private_key1:
            raise MissingFieldException(message=Message.PRIVATE_KEY1_REQUIRED_MSG)
        
        if not self.private_key2:
            raise MissingFieldException(message=Message.PRIVATE_KEY2_REQUIRED_MSG)
        
        if not self.aes_key_user:
            raise MissingFieldException(message=Message.AES_KEY_USER_REQUIRED_MSG)
        
        if not self.aes_key_auth:
            raise MissingFieldException(message=Message.AES_KEY_AUTH_REQUIRED_MSG)
    
    @classmethod
    def from_db(cls, record: Dict[str,str]) -> Legacy:
        mapped = {CaseConverter.case_to_snake(key) : value for key, value in record.items()}
        valid_fields = cls.__dataclass_fields__.keys()
        clean = {k: v for k, v in mapped.items() if k in valid_fields}
        return cls(**clean)

