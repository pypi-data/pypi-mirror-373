from typing import Dict, Type, TypeVar, get_origin, get_args, Union, Any
from dataclasses import fields, is_dataclass
from Osdental.Shared.Utils.CaseConverter import CaseConverter
from Osdental.Exception.ControlledException import OSDException

T = TypeVar('T')

class Mapper:

    @staticmethod
    def map_data(data: Dict[str, Any], model: Type[T]) -> T:
        if not is_dataclass(model):
            raise OSDException(error=f'Target model {model} is not a dataclass', message='Mapping error')

        mapped = {CaseConverter.case_to_snake(k): v for k, v in data.items()}
        instance_data = {}
        extra = {}

        for field in fields(model):
            field_name = field.name
            field_type = field.type
            value = mapped.pop(field_name, None) 
            if value is not None:
                instance_data[field_name] = Mapper._map_value(value, field_type)

        if 'extra' in [f.name for f in fields(model)]:
            extra = mapped
            instance_data['extra'] = extra

        return model(**instance_data)

    @staticmethod
    def _map_value(value: Any, field_type: Any):
        origin = get_origin(field_type)
        args = get_args(field_type)

        if origin is Union and type(None) in args:
            actual_type = next((arg for arg in args if arg is not type(None)), None)
            return Mapper._map_value(value, actual_type)

        if origin is list:
            item_type = args[0]
            if isinstance(value, list):
                return [
                    Mapper._map_value(item, item_type)
                    for item in value
                ]
            return value 

        if is_dataclass(field_type) and isinstance(value, dict):
            return Mapper.map_data(value, field_type)

        return value
