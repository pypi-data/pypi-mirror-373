import re

class CaseConverter:
    
    @staticmethod
    def case_to_snake(key: str) -> str:
        key = re.sub(r'[\s\-\.]', '_', key) 
        key = re.sub(r'(.)([A-Z][a-z]+)', r'\1_\2', key)
        key = re.sub(r'([a-z0-9])([A-Z])', r'\1_\2', key)
        return key.lower()
    
    @staticmethod
    def snake_to_camel(key: str) -> str:
        components = key.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])
    
    @staticmethod
    def snake_to_pascal(key: str) -> str:
        components = key.split('_')
        return ''.join(x.title() for x in components)