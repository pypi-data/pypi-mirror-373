from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict
from Osdental.Models.Legacy import Legacy
from Osdental.Shared.Utils.CaseConverter import CaseConverter
from Osdental.Exception.ControlledException import MissingFieldException

@dataclass
class AuthToken:
    id_token: str
    id_user: str
    id_external_enterprise: str
    id_profile: str
    id_legacy: str
    id_item_report: str
    id_enterprise: str
    id_authorization: str
    user_full_name: str
    abbreviation: str
    aes_key_auth: str
    base_id_external_enterprise: Optional[str] = None
    mk_id_external_enterprise: Optional[str] = None
    jwt_user_key: Optional[str] = None
    legacy: Optional[Legacy] = None

    def __post_init__(self):
        required_fields = [
            'id_token', 'id_user', 'id_external_enterprise', 'id_profile',
            'id_legacy', 'id_item_report', 'id_enterprise', 'id_authorization',
            'user_full_name', 'abbreviation', 'aes_key_auth'
        ]
        missing = [f for f in required_fields if not getattr(self, f)]
        if missing:
            raise MissingFieldException(error=f"Missing required fields: {', '.join(missing)}")

        
    @classmethod
    def from_jwt(cls, payload: Dict[str,str]) -> AuthToken:
        mapped = {CaseConverter.case_to_snake(key): value for key, value in payload.items()}
        valid_fields = cls.__dataclass_fields__.keys()
        clean = {k: v for k, v in mapped.items() if k in valid_fields}
        return cls(**clean)