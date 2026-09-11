"""Input validation for the receipt splitter.
 
Every function takes raw user input and necessary context and returns a
cleaned, validated value. Invalid input raises ValueError with a message that
is printed straight to the user, and the user is prompted to enter 
a valid input.
"""

from decimal import Decimal, InvalidOperation
from .models import find_key_ci
 
 
def validate_num_people(raw: str) -> int:
    try:
        num = int(raw.strip())
    except ValueError:
        raise ValueError("Please enter a whole number.")
 
    if num <= 0:
        raise ValueError("There must be at least one person.")
 
    return num


def validate_person_name(raw: str, existing_names) -> str:
    name = raw.strip()
 
    if not name:
        raise ValueError("Name cannot be empty.")

    if not any(char.isalpha() for char in name):
        raise ValueError("Name must contain at least one letter.")
 
    if any(name.lower() == existing.lower() for existing in existing_names):
        raise ValueError("That person has already been added.")
 
    return name


def validate_item_line(raw: str) -> tuple[str, str]:
    """Split 'name, price' into its two raw halves. Each half still
    needs validate_item_name / validate_price run on it."""
    if "," not in raw:
        raise ValueError(
            "Please enter the item in the format: name, price (comma-separated)."
        )
 
    name, price = raw.split(",", 1)
    return name.strip(), price.strip()


def validate_item_name(raw: str, item_names: list[str], need_existing: bool) -> str:
    name = raw.strip()
 
    if not name:
        raise ValueError("You must include an item name.")

    if not need_existing:
        if any(name.lower() == existing.lower() for existing in item_names):
            raise ValueError("That item has already been added.")
    else:
        if not any(name.lower() == existing.lower() for existing in item_names):
            raise ValueError("Please enter an existing item name.")
 
    return name


def validate_item(raw: str, items) -> tuple[str, Decimal]:
    raw_name, raw_price = validate_item_line(raw)
    name = validate_item_name(raw_name, items, False)
    price = validate_price(raw_price)
    return name, price


def validate_price(raw: str) -> Decimal:
    try:
        price = Decimal(raw.strip())
    except InvalidOperation:
        raise ValueError("Price must be a valid number.")
 
    if price <= 0:
        raise ValueError("Price must be greater than 0.")
 
    return price


def validate_shared_names(raw: str, people) -> list[str]:
    names = [name.strip() for name in raw.split(",")]
 
    if any(not name for name in names):
        raise ValueError("Please enter valid names separated by commas.")
 
    if any(find_key_ci(people, name) is None for name in names):
        raise ValueError("Please only enter names that exist.")
 
    if len(names) != len(set(n.lower() for n in names)):
        raise ValueError("Please don't enter the same person more than once.")
 
    return names


def validate_yes_no(raw: str) -> bool:
    answer = raw.strip().lower()
 
    if answer not in ("y", "n"):
        raise ValueError("Please enter y or n.")
 
    return answer == "y"


def validate_percentage_charge(raw: str) -> Decimal:
    try:
        percentage_charge = Decimal(raw.strip()) / 100
    except InvalidOperation:
        raise ValueError("Please enter a valid number.")
 
    if percentage_charge < 0:
        raise ValueError("Percentage charge cannot be negative.")

    if percentage_charge > 1:
        raise ValueError("Percentage charge cannot exceed 100%.")
 
    return percentage_charge


def validate_fixed_charge(raw: str) -> Decimal:
    try:
        fixed_charge = Decimal(raw.strip())
    except InvalidOperation:
        raise ValueError("Please enter a valid number.")

    if fixed_charge < 0:
        raise ValueError("Fixed charge cannot be negative.")

    return fixed_charge


def validate_num_option(raw: str, num_options: int) -> int:
    try:
        num = int(raw.strip())
    except ValueError:
        raise ValueError("Please enter a valid number.")
    
    if num not in range(1, num_options + 1):
        raise ValueError("Please enter a number among the options given.")

    return num
