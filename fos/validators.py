"""Input validation helpers used by every module."""
import re

CATEGORIES = ("Starters", "Main Course", "Desserts", "Drinks")
MAX_QTY = 10
EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class ValidationError(Exception):
    """Raised when user input or a business rule check fails."""


def validate_name(value, field="Name"):
    value = (value or "").strip()
    if len(value) < 2 or len(value) > 60:
        raise ValidationError(f"{field} must be 2 to 60 characters long.")
    return value


def validate_email(value):
    value = (value or "").strip().lower()
    if not EMAIL_PATTERN.match(value):
        raise ValidationError("Email address is not valid.")
    return value


def validate_phone(value):
    value = (value or "").strip()
    if not (value.isdigit() and len(value) == 10):
        raise ValidationError("Phone number must contain exactly 10 digits.")
    return value


def validate_price(value):
    try:
        price = round(float(value), 2)
    except (TypeError, ValueError):
        raise ValidationError("Price must be a number greater than 0.")
    if price <= 0 or price > 5000:
        raise ValidationError("Price must be a number greater than 0.")
    return price


def validate_category(value):
    for category in CATEGORIES:
        if (value or "").strip().lower() == category.lower():
            return category
    raise ValidationError("Category must be one of: " + ", ".join(CATEGORIES) + ".")


def validate_quantity(value):
    try:
        qty = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"Quantity must be between 1 and {MAX_QTY}.")
    if qty < 1 or qty > MAX_QTY:
        raise ValidationError(f"Quantity must be between 1 and {MAX_QTY}.")
    return qty


def validate_id(value, field="ID"):
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValidationError(f"{field} must be a positive whole number.")
    if number < 1:
        raise ValidationError(f"{field} must be a positive whole number.")
    return number
