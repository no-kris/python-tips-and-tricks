from datetime import datetime


def format_date(date_str: str, fmt: str = "%B %d, %Y (%A)"):
    """
    Parses an ISO format date string and returns it formatted.
    """
    dt = datetime.fromisoformat(date_str)
    return dt.strftime(fmt)
