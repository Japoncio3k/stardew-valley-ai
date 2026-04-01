from datetime import datetime


def print_with_timestamp(*args: object) -> None:
    """Prints a message with a timestamp."""
    date = datetime.now().strftime("%H:%M:%S")
    print(f"[{date}]", *args)
