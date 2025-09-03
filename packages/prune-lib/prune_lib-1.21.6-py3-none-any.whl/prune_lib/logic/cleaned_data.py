import re


def clean_phone(phone: str) -> str | None:
    if phone and not re.match(r"^[\d\+\- \(\)]{6,20}$", phone):
        raise ValueError("invalid_phone_number")
    return phone
