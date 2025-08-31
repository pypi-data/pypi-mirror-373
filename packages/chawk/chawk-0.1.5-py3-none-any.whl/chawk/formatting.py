from datetime import datetime
from re import sub


def format_date(date_string: str) -> str:
    """Takes in the date format blackboard uses and changes it to MM/DD/YYYY

    Args:
        date_string (str): Timestamp in ISO 8601. Example: "2024-06-27T14:15:14.634Z"

    Returns:
        str: Example "06/27/2024"
    """

    try:
        datetime_obj = datetime.strptime(
            date_string, "%Y-%m-%dT%H:%M:%S.%fZ"
        ).strftime("%m-%d-%Y")

        return datetime_obj
    except Exception:
        return ""



def get_datetime_now() -> str:
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d %H:%M:%S")
    return formatted_datetime

def remove_parentheses_content(text: str) -> str:
    # Remove everything inside parentheses including the parentheses themselves
    result = sub(r"\s*\(.*?\)", "", text)
    return result.strip()