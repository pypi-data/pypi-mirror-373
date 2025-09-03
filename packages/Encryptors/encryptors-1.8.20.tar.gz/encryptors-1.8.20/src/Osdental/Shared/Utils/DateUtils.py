from datetime import datetime, date, timedelta
import calendar

class DateUtils:

    @staticmethod
    def now() -> datetime:
        """Returns the current date and time."""
        return datetime.now()

    @staticmethod
    def today() -> date:
        """Returns the current date."""
        return date.today()

    @staticmethod
    def current_year() -> int:
        """Returns the current year as an integer."""
        return date.today().year

    @staticmethod
    def current_month() -> int:
        """Returns the current month as an integer."""
        return date.today().month

    @staticmethod
    def parse_date(text: str, fmt: str = "%Y-%m-%d") -> date:
        """Parses a date string into a `date` object using the specified format."""
        return datetime.strptime(text, fmt).date()

    @staticmethod
    def parse_datetime(text: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
        """Parses a datetime string into a `datetime` object using the specified format."""
        return datetime.strptime(text, fmt)

    @staticmethod
    def format_date(d: date, fmt: str = "%Y-%m-%d") -> str:
        """Formats a `date` object into a string using the specified format."""
        return d.strftime(fmt)

    @staticmethod
    def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
        """Formats a `datetime` object into a string using the specified format."""
        return dt.strftime(fmt)

    @staticmethod
    def add_days(d: date, days: int) -> date:
        """Returns a new date by adding the specified number of days."""
        return d + timedelta(days=days)

    @staticmethod
    def subtract_days(d: date, days: int) -> date:
        """Returns a new date by subtracting the specified number of days."""
        return d - timedelta(days=days)

    @staticmethod
    def days_between(start: date, end: date) -> int:
        """Returns the number of days between two dates."""
        return (end - start).days

    @staticmethod
    def is_past(d: date) -> bool:
        """Returns True if the given date is in the past."""
        return d < date.today()

    @staticmethod
    def is_future(d: date) -> bool:
        """Returns True if the given date is in the future."""
        return d > date.today()

    @staticmethod
    def is_today(d: date) -> bool:
        """Returns True if the given date is today."""
        return d == date.today()

    @staticmethod
    def start_of_month(d: date) -> date:
        """Returns the first day of the month for the given date."""
        return d.replace(day=1)

    @staticmethod
    def end_of_month(d: date) -> date:
        """Returns the last day of the month for the given date."""
        last_day = calendar.monthrange(d.year, d.month)[1]
        return d.replace(day=last_day)

    @staticmethod
    def start_of_year(d: date) -> date:
        """Returns the first day of the year for the given date."""
        return d.replace(month=1, day=1)

    @staticmethod
    def end_of_year(d: date) -> date:
        """Returns the last day of the year for the given date."""
        return d.replace(month=12, day=31)

    @staticmethod
    def to_iso_string(dt: datetime) -> str:
        """Converts a `datetime` object to ISO 8601 format string."""
        return dt.isoformat()

    @staticmethod
    def from_iso_string(text: str) -> datetime:
        """Parses an ISO 8601 format string into a `datetime` object."""
        return datetime.fromisoformat(text)

    @staticmethod
    def weekday_name(d: date) -> str:
        """Returns the name of the weekday for the given date (e.g., 'Monday')."""
        return d.strftime("%A")

    @staticmethod
    def month_name(d: date) -> str:
        """Returns the full name of the month for the given date (e.g., 'January')."""
        return d.strftime("%B")

    @staticmethod
    def get_ttl_for_midnight() -> int:
        """Returns the number of seconds remaining until the next midnight."""
        now = datetime.now()
        tomorrow = now + timedelta(days=1)
        midnight = datetime(year=tomorrow.year, month=tomorrow.month, day=tomorrow.day)
        ttl = (midnight - now).seconds
        return ttl
