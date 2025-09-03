import uuid
from typing import Dict

class DataUtils:

    @staticmethod
    def normalize_uuid_value(value):
        if isinstance(value, str):
            try:
                return str(uuid.UUID(value)).lower()
            except ValueError:
                return value
        return value

    @staticmethod
    def normalize_uuids_dict(data: Dict[str,str]) -> Dict[str,str]:
        return {k: DataUtils.normalize_uuid_value(v) for k, v in data.items()}