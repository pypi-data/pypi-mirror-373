import random
import string

class CodeGenerator:

    @staticmethod
    def generate_numeric_code(length:int = 6) -> str:
        nums = string.digits        
        return ''.join(random.choices(nums,k=length)) 
    
    @staticmethod
    def generate_alpha_code(length:int = 6) -> str:
        return ''.join(random.choices(string.ascii_letters, k=length))
    
    @staticmethod
    def generate_uppercase_code(length:int = 6) -> str:
        return ''.join(random.choices(string.ascii_uppercase, k=length))
    
    @staticmethod
    def generate_lowercase_code(length:int = 6) -> str:
        return ''.join(random.choices(string.ascii_lowercase, k=length))
    
    @staticmethod
    def generate_alphanumeric_code(length: int = 6) -> str:
        chars = string.ascii_letters + string.digits  
        return ''.join(random.choices(chars, k=length))
    
    @staticmethod
    def generate_secure_code(length: int = 6) -> str:
        chars = string.ascii_letters + string.digits + string.punctuation
        return ''.join(random.choices(chars, k=length))