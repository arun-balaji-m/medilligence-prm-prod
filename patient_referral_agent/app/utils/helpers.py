from datetime import datetime
from typing import Optional


def parse_flexible_date(date_str: str) -> Optional[str]:

    if not date_str or date_str == "null":
        return None


    if len(date_str) == 10 and date_str[4] == '-' and date_str[7] == '-':
        try:
            datetime.strptime(date_str, '%Y-%m-%d')
            return date_str
        except ValueError:
            pass


    formats = [
        '%Y-%m-%d',  # 2020-10-02
        '%d-%m-%Y',  # 02-10-2020
        '%m/%d/%Y',  # 10/02/2020
        '%d/%m/%Y',  # 02/10/2020
        '%d %B %Y',  # 2 October 2020
        '%B %d, %Y',  # October 2, 2020
        '%d %b %Y',  # 2 Oct 2020
        '%b %d, %Y',  # Oct 2, 2020
        '%Y/%m/%d',  # 2020/10/02
    ]

    # Clean the string
    date_str = date_str.strip()


    import re
    date_str = re.sub(r'(\d+)(st|nd|rd|th)', r'\1', date_str)

    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue


    try:
        from dateutil import parser
        dt = parser.parse(date_str, dayfirst=True)
        return dt.strftime('%Y-%m-%d')
    except:
        pass

    return None


def validate_required_fields(patient_data: dict, required: list) -> bool:
    """Check if all required fields have non-null, non-empty values"""
    for field in required:
        value = patient_data.get(field)
        if not value or value == "null" or value == "none":
            return False
    return True