import hashlib
from Osdental.Shared.Enums.Constant import Constant

class SHA512:

    @staticmethod
    def hash_password(password: str) -> str:
        """Generates the SHA-512 hash of a password."""
        hash_object = hashlib.sha512(password.encode(Constant.DEFAULT_ENCODING))
        hashed_password = hash_object.hexdigest()
        return hashed_password

    @staticmethod
    def verify_password(hash_password: str, password: str) -> bool:
        """Checks if the provided password matches the stored hash."""
        return SHA512.hash_password(password) == hash_password