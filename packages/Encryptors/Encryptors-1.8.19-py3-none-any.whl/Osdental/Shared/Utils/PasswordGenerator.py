import random
import string
from Osdental.Shared.Enums.Message import Message

class PasswordGenerator:

    @staticmethod
    def generate_simple(length: int = 12) -> str:
        valid_characters = string.ascii_letters + string.digits + '!@#$%^&*()-_=+[]{}|:,.?'
        password = ''.join(random.choice(valid_characters) for _ in range(length))
        return password

    @staticmethod
    def generate(length: int = 12, use_uppercase: bool = True, use_digits: bool = True, use_symbols: bool = True, exclude_ambiguous: bool = True) -> str:
        lowercase = string.ascii_lowercase
        uppercase = string.ascii_uppercase if use_uppercase else ''
        digits = string.digits if use_digits else ''
        symbols = string.punctuation if use_symbols else ''

        if exclude_ambiguous:
            ambiguous = 'Il1O0|'
            lowercase = ''.join(c for c in lowercase if c not in ambiguous)
            uppercase = ''.join(c for c in uppercase if c not in ambiguous)
            digits = ''.join(c for c in digits if c not in ambiguous)
            symbols = ''.join(c for c in symbols if c not in ambiguous)

        all_chars = lowercase + uppercase + digits + symbols
        if not all_chars:
            raise ValueError(Message.NO_PASSWORD_CHARACTERS_MSG)

        return ''.join(random.choice(all_chars) for _ in range(length))

    @staticmethod
    def generate_with_rules(min_upper: int = 1, min_digits: int = 1, min_symbols: int = 1, length: int = 12) -> str:
        if length < (min_upper + min_digits + min_symbols):
            raise ValueError(Message.INSUFFICIENT_LENGTH_MSG)

        password = []
        password.extend(random.choices(string.ascii_uppercase, k=min_upper))
        password.extend(random.choices(string.digits, k=min_digits))
        password.extend(random.choices(string.punctuation, k=min_symbols))
        password.extend(random.choices(string.ascii_lowercase, k=length - len(password)))

        random.shuffle(password)
        return ''.join(password)
