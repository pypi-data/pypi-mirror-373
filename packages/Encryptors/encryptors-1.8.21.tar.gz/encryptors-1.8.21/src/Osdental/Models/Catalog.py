from __future__ import annotations
from dataclasses import dataclass
from typing import Dict
from Osdental.Shared.Utils.CaseConverter import CaseConverter

@dataclass
class Catalog:
    id_catalog: str
    name_catalog: str
    id_detail: str
    code: str
    value: str

    @classmethod
    def from_db(cls, record: Dict[str,str]) -> Catalog:
        mapped = {CaseConverter.case_to_snake(key) : value for key, value in record.items()}
        valid_fields = cls.__dataclass_fields__.keys()
        clean = {k: v for k, v in mapped.items() if k in valid_fields}
        return cls(**clean)