import inspect
import json
from functools import wraps
from typing import Callable, Tuple, Optional, Union, Dict, Any
from uuid import UUID
from graphql import GraphQLResolveInfo
from graphql import OperationType
from Osdental.Encryptor.Jwt import JWT
from Osdental.Exception.ControlledException import UnauthorizedException, ProfilePermissionDeniedException, InvalidFormatException
from Osdental.Handlers.DBSecurityQuery import DBSecurityQuery
from Osdental.Models.Legacy import Legacy
from Osdental.Handlers.Instances import jwt_user_key, aes
from Osdental.Models.Token import AuthToken
from Osdental.Shared.Enums.Message import Message
from Osdental.Shared.Enums.Profile import Profile

db_security_query = DBSecurityQuery()

async def validate_token(token_id: str, user_id: str):
    is_auth = await db_security_query.validate_auth_token(token_id, user_id)
    if not is_auth:
        raise UnauthorizedException(message=Message.PORTAL_ACCESS_RESTRICTED_MSG, error=Message.PORTAL_ACCESS_RESTRICTED_MSG)
    

def check_profile_permission(allowed_permissions: str | Tuple[str, ...] | None, requested_permission: str) -> bool:
    SUPER_PROFILES = (Profile.SUPER_ADMIN, Profile.ADMIN_OSD)

    if allowed_permissions is None:
        allowed = ()
    elif isinstance(allowed_permissions, str):
        allowed = (allowed_permissions,)
    else:
        allowed = allowed_permissions

    total_allowed = set(allowed) | set(SUPER_PROFILES)
    return requested_permission in total_allowed


async def decrypted_token(info: GraphQLResolveInfo = None, legacy: Legacy = None, mutate: bool = True) -> Optional[AuthToken]:
    operation_type = info.operation.operation
    user_token_encrypted = info.context.get('user_token')

    if not user_token_encrypted:
        return None

    user_token = aes.decrypt(legacy.aes_key_user, user_token_encrypted)
    payload = JWT.extract_payload(user_token, jwt_user_key)
    payload['legacy'] = legacy
    payload['jwt_user_key'] = jwt_user_key
    token = AuthToken.from_jwt(payload)
    token.base_id_external_enterprise = token.id_external_enterprise
    await validate_token(token.id_token, token.id_user)

    headers = info.context.get('headers', {})
    id_external_mk = headers.get('dynamicClientId')

    is_marketing = token.abbreviation.startswith(Profile.MARKETING)
    should_use_zero_uuid = (
        token.abbreviation.startswith((Profile.SUPER_ADMIN, Profile.ADMIN_OSD))
        and operation_type == OperationType.QUERY and mutate
    )
    should_use_mk_header = is_marketing and id_external_mk

    if should_use_zero_uuid:
        token.id_external_enterprise = str(UUID(int=0))
    elif should_use_mk_header:
        token.id_external_enterprise = aes.decrypt(token.aes_key_auth, id_external_mk)
        token.mk_id_external_enterprise = id_external_mk

    return token


def decrypted_data(aes_data: Optional[str], aes_key_auth: str, token: AuthToken) -> Optional[Dict[str, Any]]:
    data = None
    if aes_data is not None:
        decrypted_data = aes.decrypt(aes_key_auth, aes_data)
        if isinstance(decrypted_data, str):
            try:
                data = json.loads(decrypted_data)
            except Exception:
                raise InvalidFormatException(message=Message.INVALID_AES_JSON_FORMAT_MSG)
        elif isinstance(decrypted_data, dict):
            data = decrypted_data
        else:
            raise UnauthorizedException(message=Message.UNEXPECTED_DECRYPTED_DATA_FORMAT_MSG)
        # Overwrite enterprise ID if applicable
        external_enterprise_req = data.get('idExternalEnterprise')
        if external_enterprise_req and token:
            token.id_external_enterprise = external_enterprise_req

    return data

def process_encrypted_data(mutate: bool = True, allowed_permissions: Optional[Union[str, Tuple[str, ...]]] = None):
    def decorator(func: Callable):
        @wraps(func)
        async def wrapper(self, info: GraphQLResolveInfo = None, aes_data: str = None, **rest_kwargs):
            legacy = await db_security_query.get_legacy_data()
            token = await decrypted_token(info, legacy, mutate) if info else None

            if allowed_permissions and token:
                is_authorized = check_profile_permission(allowed_permissions, token.abbreviation)
                if not is_authorized:
                    raise ProfilePermissionDeniedException(message=Message.PROFILE_PERMISSION_DENIED_MSG)

            data = decrypted_data(aes_data, legacy.aes_key_auth, token)
            
            # Introspect function params
            sig = inspect.signature(func)
            kwargs_to_pass = {}
            if 'token' in sig.parameters and token:
                kwargs_to_pass['token'] = token
            if 'data' in sig.parameters and data:
                kwargs_to_pass['data'] = data

            return await func(self, **kwargs_to_pass, **rest_kwargs)

        return wrapper
    return decorator