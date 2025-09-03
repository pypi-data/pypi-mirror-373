import re

class TextProcessor:

    @staticmethod
    def to_lower(text: str) -> str:
        """Converts the text to lowercase."""
        return text.lower()

    @staticmethod
    def to_upper(text: str) -> str:
        """Converts the text to uppercase."""
        return text.upper()

    @staticmethod
    def capitalize(text: str) -> str:
        """Capitalizes the first character of the text."""
        return text.capitalize()

    @staticmethod
    def title_case(text: str) -> str:
        """Capitalizes the first letter of each word in the text."""
        return text.title()
    
    @staticmethod
    def is_numeric(text: str) -> bool:
        """Checks if the text consists only of digits."""
        return text.isdigit()

    @staticmethod
    def is_alpha(text: str) -> bool:
        """Checks if the text consists only of alphabetic characters."""
        return text.isalpha()

    @staticmethod
    def remove_whitespace(text: str) -> str:
        """Removes extra whitespace from the text."""
        return ' '.join(text.split())

    @staticmethod
    def remove_special_chars(text: str, allowed: str = '') -> str:
        """Removes all special characters from the text, except those allowed."""
        return re.sub(fr'[^\w\s{re.escape(allowed)}]', '', text)
    
    @staticmethod
    def concatenate(*parts: str, sep: str = ' ') -> str:
        """Concatenates multiple string parts using the given separator."""
        return sep.join(parts)
    
    @staticmethod
    def contains(text: str, sub: str, case_sensitive: bool = True) -> bool:
        """Checks if the text contains the specified substring."""
        return sub in text if case_sensitive else sub.lower() in text.lower()
    
    @staticmethod
    def clean_word(text: str) -> str:
        """Cleans the text by removing special characters and converting to lowercase."""
        text = text.lower().strip()
        return re.sub(r'[^a-z0-9\s]', '', text)

    @staticmethod
    def clean_slug(text: str, sep: str = '_') -> str:
        """Cleans the text and converts it into a slug, using the given separator."""
        text = TextProcessor.clean_word(text)
        return sep.join(text.split())

    @staticmethod
    def remove_prefix(text: str, prefix: str) -> str:
        """Removes the specified prefix from the text if present."""
        return text[len(prefix):] if text.startswith(prefix) else text

    @staticmethod
    def remove_suffix(text: str, suffix: str) -> str:
        """Removes the specified suffix from the text if present."""
        return text[:-len(suffix)] if text.endswith(suffix) else text

    @staticmethod
    def truncate(text: str, length: int, ellipsis: bool = False) -> str:
        """Truncates the text to a specific length, optionally adding ellipsis."""
        return text[:length] + ('...' if ellipsis and len(text) > length else "")

    @staticmethod
    def slugify(text: str) -> str:
        """
        Converts the text to a URL-friendly slug format:
        - Normalizes
        - Removes non-word characters
        - Converts to lowercase
        - Replaces spaces and hyphens with single hyphen
        """
        text = TextProcessor.normalize(text)
        text = re.sub(r"[^\w\s-]", "", text).strip().lower()
        return re.sub(r"[-\s]+", "-", text)

    @staticmethod
    def normalize(text: str) -> str:
        """Placeholder for text normalization (e.g., unicode normalization)."""
        return re.sub(r'\s+', ' ', text.strip())

    
