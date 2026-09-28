"""Input validation for the receipt splitter.

Every function takes raw user input and necessary context and returns a
cleaned, validated value. Invalid input raises ValueError with a message that
is printed straight to the user, and the user is prompted to enter
a valid input.
"""

from decimal import Decimal, InvalidOperation

from .models import find_key_ci


def validate_person_names(raw: str) -> list[str]:
    raw = raw.strip()
    if not raw:
        raise ValueError("Please enter at least one person.")

    names = [name.strip() for name in raw.split(",")]

    if len(names) != len({n.lower() for n in names}):
        raise ValueError("Please don't enter the same person more than once.")

    for name in names:
        if not name:
            raise ValueError("Please enter valid names separated by commas.")

        if not any(char.isalpha() for char in name):
            raise ValueError("Names must contain at least one letter.")

    return names


def validate_new_person_name(raw: str, existing_names) -> str:
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


def validate_percentage_charge(raw: str) -> tuple[Decimal, str | None]:
    if " " in raw.strip():
        val, label = raw.strip().split(" ", 1)
        val = val.strip()
        label = label.strip()

        if not any(char.isalpha() for char in label):
            raise ValueError("Please enter a charge label with at least one letter.")

    else:
        val = raw.strip()
        label = None

    try:
        pct = Decimal(val) / 100
    except InvalidOperation:
        raise ValueError("Please enter a valid number.")

    if pct < 0:
        raise ValueError("Percentage charge cannot be negative.")

    if pct > 1:
        raise ValueError("Percentage charge cannot exceed 100%.")

    return (pct, label)


def validate_fixed_charge(raw: str) -> tuple[Decimal, str | None]:
    if " " in raw.strip():
        val, label = raw.strip().split(" ", 1)
        val = val.strip()
        label = label.strip()

        if not any(char.isalpha() for char in label):
            raise ValueError("Please enter a charge label with at least one letter.")

    else:
        val = raw.strip()
        label = None

    try:
        fixed = Decimal(val)
    except InvalidOperation:
        raise ValueError("Please enter a valid number.")

    if fixed < 0:
        raise ValueError("Fixed charge cannot be negative.")

    return (fixed, label)


def validate_num_option(raw: str, num_options: int) -> int:
    try:
        num = int(raw.strip())
    except ValueError:
        raise ValueError("Please enter a valid number.")

    if num not in range(1, num_options + 1):
        raise ValueError("Please enter a number among the options given.")

    return num


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


def validate_fast_split_extra_charges(raw: str) -> list[tuple[str, str | None]]:
    raw = raw.strip()
    if not raw:
        return []

    tokens = [c.strip() for c in raw.split(",")]

    if any(not t for t in tokens):
        raise ValueError("Please enter valid charges separated by commas.")

    validated_charges = []

    for token in tokens:
        if " " in token:
            val_str, label = token.split(" ", 1)
            val_str = val_str.strip()
            label = label.strip()

            if not any(char.isalpha() for char in label):
                raise ValueError("Please enter charge labels with at least one letter.")

        else:
            val_str = token
            label = None

        if not val_str:
            raise ValueError("Please enter valid charges separated by commas.")

        ends_in_percent = val_str.endswith("%")

        if "%" in val_str[:-1]:
            raise ValueError("Please enter valid percentages with '%' at the end.")

        val_num = val_str.removesuffix("%") if ends_in_percent else val_str

        try:
            value = Decimal(val_num)
        except InvalidOperation:
            raise ValueError("Please enter valid numbers for charges.")

        if value <= 0:
            raise ValueError("Charges must be greater than zero. ")

        if value.as_tuple().exponent < -2:
            raise ValueError("Charges cannot have more than 2 decimal places.")

        if ends_in_percent and value > 100:
            raise ValueError("Percentage charge must not exceed 100%.")

        validated_charges.append((val_str, label))

    return validated_charges
