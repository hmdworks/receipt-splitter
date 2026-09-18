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

    if price.as_tuple().exponent < -2:
        raise ValueError("Price must have at most 2 decimal places.")

    return price


def validate_shared_names(raw: str, people) -> list[str]:
    raw = raw.strip()
    
    if raw.lower() == "all":
        return list(people.keys())
    
    names = [name.strip() for name in raw.split(",")]

    if any(not name for name in names):
        raise ValueError("Please enter valid names separated by commas.")

    if any(find_key_ci(people, name) is None for name in names):
        raise ValueError("Please only enter names that exist.")

    if len(names) != len({n.lower() for n in names}):
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


def validate_weight_input(raw: str) -> Decimal:
    try:
        weight = Decimal(raw.strip()) / 100
    except InvalidOperation:
        raise ValueError("Please enter a valid percentage.")

    if weight <= 0:
        raise ValueError("Please enter a percentage weight greater than zero for each person.")
    
    if weight >= 1:
        raise ValueError("Percentage weight must not be greater than or equal to 100.")

    return weight


def validate_item_weights_add_to_one(weights: list[Decimal]) -> bool:
    total = sum(weights)

    if total != 1:
        raise ValueError(f"Percentage weights add up to {total * 100}, but must add up to 100.")

    return True


def validate_shares_input(raw: str) -> Decimal:
    raw = raw.strip()

    if not raw.isdigit() or int(raw) <= 0:
        raise ValueError("Please enter an integer share greater than zero.")

    return Decimal(raw)


def validate_fast_split_line(raw: str, items: dict) -> list[str | Decimal]:
    if not raw.strip():
        if not items:
            raise ValueError("Please include at least one item.")
        else:
            return []

    details = [detail.strip() for detail in raw.split(",")]

    if len(details) <= 2:
        raise ValueError("Please enter sufficient details.")

    item, price, *names = details

    if any(not detail for detail in details):
        raise ValueError("Please enter valid details separated by commas.")

    if any(item.lower() == i.lower() for i in items):
        raise ValueError("That item has already been added.")

    if not any(char.isalpha() for char in item):
        raise ValueError("Item name must contain at least one letter.")

    clean_price = validate_price(price)
    details[1] = clean_price

    for name in names:
        if not any(char.isalpha() for char in name):
            raise ValueError("Person names must contain at least one letter.")

    if len(names) != len({n.lower() for n in names}):
        raise ValueError("Please don't enter the same person more than once.")

    return details


def validate_fast_split_extra_charges(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        return []

    charges = [c.strip() for c in raw.split(",")]

    if any(not c for c in charges):
        raise ValueError("Please enter valid charges separated by commas.")

    for charge in charges:
        ends_in_percent = charge.endswith("%")

        if "%" in charge[:-1]:
            raise ValueError("Please enter valid percentages with '%' at the end.")

        charge_num = charge.removesuffix("%") if ends_in_percent else charge

        try:
            value = Decimal(charge_num)
        except InvalidOperation:
            raise ValueError("Please enter valid numbers for charges.")

        if value <= 0:
            raise ValueError("Charges must be greater than zero. ")

        if value.as_tuple().exponent < -2:
            raise ValueError("Charges cannot have more than 2 decimal places.")

        if ends_in_percent and value > 100:
            raise ValueError("Percentage charge must not exceed 100%.")

    return charges
