"""Input validation for the receipt splitter.
 
Every function takes raw user input (plus whatever context it needs to
check against - e.g. names already added) and returns a cleaned,
validated value. Invalid input raises ValueError with a message that
is printed straight to the user, and the user is prompted to enter 
a valid input.
"""

from decimal import Decimal, InvalidOperation
 
 
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
 
    if name in existing_names:
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


def validate_item_name(raw: str, existing_names) -> str:
    name = raw.strip()
 
    if not name:
        raise ValueError("You must include an item name.")
 
    if name in existing_names:
        raise ValueError("That item has already been added.")
 
    return name


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
 
    if any(name not in people for name in names):
        raise ValueError("Please only enter names that exist.")
 
    if len(names) != len(set(names)):
        raise ValueError("Please don't enter the same person more than once.")
 
    return names


def validate_yes_no(raw: str) -> bool:
    answer = raw.strip().lower()
 
    if answer not in ("y", "n"):
        raise ValueError("Please enter y or n.")
 
    return answer == "y"


def validate_service_rate(raw: str) -> Decimal:
    try:
        service_rate = Decimal(raw.strip()) / 100
    except InvalidOperation:
        raise ValueError("Please enter a valid number.")
 
    if service_rate < 0:
        raise ValueError("Service charge cannot be negative.")

    if service_rate > 1:
        raise ValueError("Service charge cannot exceed 100%.")
 
    return service_rate