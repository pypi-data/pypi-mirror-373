from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from Osdental.Shared.Utils.CaseConverter import CaseConverter
from Osdental.Exception.ControlledException import MissingFieldException
from Osdental.Shared.Enums.Message import Message

@dataclass
class CdataIntegration:
    id_cdata_integration: str
    exp_token: int
    key_private: str

    def __post_init__(self):
        if not self.id_cdata_integration:
            raise MissingFieldException(message=Message.ID_CDATA_INTEGRATION_REQUIRED)
        
        if not self.exp_token:
            raise MissingFieldException(message=Message.EXP_TIME_REQUIRED)                
        
        if not self.key_private:
            raise MissingFieldException(message=Message.KEY_PRIVATE_REQUIRED)
    
    @classmethod
    def from_db(cls, record: Dict[str,str]) -> CdataIntegration:
        mapped = {CaseConverter.case_to_snake(key) : value for key, value in record.items()}
        valid_fields = cls.__dataclass_fields__.keys()
        clean = {k: v for k, v in mapped.items() if k in valid_fields}
        return cls(**clean)

@dataclass
class CdataInfo:
    token_type: str
    iss: str

    @classmethod
    def from_db(cls, record: Dict[str,str]) -> CdataInfo:
        mapped = {CaseConverter.case_to_snake(key) : value for key, value in record.items()}
        valid_fields = cls.__dataclass_fields__.keys()
        clean = {k: v for k, v in mapped.items() if k in valid_fields}
        return cls(**clean)