import datetime
def current_date() -> str:
    """
    Return current date as a string.
    """
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
