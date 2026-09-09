"""Command-line interface for the receipt splitter."""

from .calculator import split_cost, apply_extra_charges, apply_rounding
from . import validation
from .models import Receipt, Charge, ChargeType
from .formatter import show_receipt, show_amount_owed

import time
from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings


# add option to exit with Esc
kb = KeyBindings()

@kb.add("escape")
def _(event):
    event.app.exit(exception=KeyboardInterrupt)

session = PromptSession()

# add confirmation on Esc
def confirm_exit() -> bool:
    confirm_kb = KeyBindings()

    @confirm_kb.add("escape")
    def _(event):
        event.app.exit(result=True)

    @confirm_kb.add("enter")
    def _(event):
        event.app.exit(result=False)

    return session.prompt(
        "\nPress Esc again to exit, or Enter to continue: ",
        key_bindings=confirm_kb,
    )


def get_input(prompt: str) -> str:
    while True:
        try:
            return session.prompt(prompt, key_bindings=kb)
        except KeyboardInterrupt:
            if confirm_exit():
                raise

            clear_lines(3)


def get_validated_input(prompt, validator, *args, **kwargs):
    error = False
    while True:
        try:
            value = validator(get_input(prompt), *args, **kwargs)
            clear_line()
            return value
        except ValueError as e:
            clear_line()  # clear prompt
            if error:
                clear_lines(2)  # clear previous error plus blank line
            print(e)
            print()
            error = True


# ANSI codes to clear inputs
def clear_line() -> None:
    print("\033[1A\033[2K", end="")


def clear_lines(count: int) -> None:
    for _ in range(count):
        clear_line()


def clear_screen() -> None:
    print("\033[2J\033[3J\033[H", end="")


def display_header(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))
    print()


def display_start_menu() -> None:
    display_header("ReceiptSplitter")
    print("Split your bill, fairly.\n")
    print("Press Enter to start!")
    print("Press Esc anytime to quit.\n")

    get_input("")


def refresh_receipt(receipt: Receipt) -> None:
    clear_screen()
    show_receipt(receipt)
    print()


# --------------------------------------------------------------------------------------
# People
# --------------------------------------------------------------------------------------

def display_people(receipt: Receipt) -> None:
    display_header("People")

    for i, person in enumerate(receipt.people.values(), 1):
        print(f"{i}. {person.name}")


def edit_person(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)

    people = list(receipt.people.values())

    choice = get_input(
        "\nEnter person number to edit (or press Enter to go back): "
    )

    if not choice:
        return

    try:
        person = people[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid person number.")
        return

    new_name = get_validated_input(
        f"New name [{person.name}]: ",
        validation.validate_person_name,
        receipt.people
    )

    receipt.rename_person(person.name, new_name)


def delete_person(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)

    people = list(receipt.people.values())

    choice = get_input(
        "\nEnter person number to delete (or press Enter to go back): "
    )

    if not choice:
        return

    try:
        person = people[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid person number.")
        return

    receipt.remove_person(person.name)


def add_person(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)
    print()

    name = get_validated_input(
        "Name: ",
        validation.validate_person_name,
        receipt.people
    )

    receipt.add_person(name)


def get_people(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)

    # validate number of people
    num_people = get_validated_input(
        "How many people? ",
        validation.validate_num_people,
    )

    clear_screen()
    display_people(receipt)

    # get each person's name and validate
    for i in range(num_people):

        name = get_validated_input(
            f"Person {i+1}: ",
            validation.validate_person_name,
            receipt.people
        )

        receipt.add_person(name)

    while True:
        clear_screen()
        display_people(receipt)
        print("\n[a] Add  [e] Edit  [d] Delete  [c] Continue")

        choice = get_input("> ").lower()

        if choice == "a":
            add_person(receipt)

        elif choice == "e":
            edit_person(receipt)

        elif choice == "d":
            delete_person(receipt)

        elif choice == "c":
            clear_screen()
            return

        else:
            print("Please enter a, e, d, or c.")


# --------------------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------------------

def display_items(receipt: Receipt) -> None:
    display_header("Items")

    for i, item in enumerate(receipt.items.values(), 1):
        print(f"{i}. {item.name} - £{item.price:.2f}")


def add_item(receipt: Receipt) -> None:
    clear_screen()
    display_items(receipt)
    print()

    name, price = get_validated_input(
        "Add item (name, price): ",
        validation.validate_item,
        receipt.items,
    )

    receipt.add_item(name, price)


def edit_item(receipt: Receipt) -> None:
    items = list(receipt.items.values())

    clear_screen()
    display_items(receipt)

    choice = get_input(
        "\nEnter item number to edit (or press Enter to go back): "
    )

    if not choice:
        return

    try:
        item = items[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid item number.")
        return

    while True:
        new_name = get_input(
            f"Name [{item.name}] (press Enter if no change): "
        )

        if not new_name:
            new_name = item.name
            break

        try:
            new_name = validation.validate_item_name(
                new_name,
                receipt.items,
            )
            break
        except ValueError as e:
            print(e)

    while True:
        new_price = get_input(
            f"Price [{item.price:.2f}] (press Enter if no change): "
        )

        if not new_price:
            new_price = item.price
            break

        try:
            new_price = validation.validate_price(new_price)
            break
        except ValueError as e:
            print(e)

    receipt.edit_item(
        item.name,
        new_name,
        new_price,
    )


def delete_item(receipt: Receipt) -> None:
    items = list(receipt.items.values())

    clear_screen()
    display_items(receipt)

    choice = get_input(
        "\nEnter item number to delete (or press Enter to go back): "
    )

    if not choice:
        return

    try:
        item = items[int(choice) - 1]
    except (ValueError, IndexError):
        print("Invalid item number.")
        return

    receipt.remove_item(item.name)


def get_items(receipt: Receipt) -> None:
    while True:
        add_item(receipt)

        clear_screen()
        display_items(receipt)
        print()

        # ask to add another item
        add_another = get_validated_input(
            "Add another item? (y/n): ",
            validation.validate_yes_no
        )

        if not add_another:
            break

    while True:
        clear_screen()
        display_items(receipt)

        print("\n[a] Add  [e] Edit  [d] Delete  [c] Continue")

        choice = get_input("> ").lower()

        if choice == "a":
            add_item(receipt)

        elif choice == "e":
            edit_item(receipt)

        elif choice == "d":
            delete_item(receipt)

        elif choice == "c":
            return

        else:
            print("Please enter a, e, d, or c.")


# --------------------------------------------------------------------------------------
# Shared items
# --------------------------------------------------------------------------------------           

def find_item(items, name):
    name = name.strip()

    for item in items:
        if item.name == name:
            return item

    raise ValueError("Item not found.")


def edit_shared_by(receipt: Receipt) -> None:
    refresh_receipt(receipt)
    
    items = list(receipt.items.values())

    choice = get_input(
        "\nEnter item name to edit (or press Enter to go back): "
    )

    if not choice:
        return

    try:
        item = find_item(items, choice)
    except ValueError as e:
        print(e)
        return

    names = get_validated_input(
        f"Who shared {item.name}? (comma-separated): ",
        validation.validate_shared_names,
        receipt.people
    )

    item.shared_by = names

    
def assign_items(receipt: Receipt) -> None:
    refresh_receipt(receipt)
    display_people(receipt)
    print()

    # ask who shared each item
    for item in receipt.items.values():
        names = get_validated_input(
                f"Who shared {item.name}? (comma-separated): ",
                validation.validate_shared_names,
                receipt.people
            )

        item.shared_by = names
        refresh_receipt(receipt)
        display_people(receipt)
        print()
            

    while True:
        refresh_receipt(receipt)

        print("\n[e] Edit  [c] Continue")

        choice = get_input("> ").lower()

        if choice == "e":
            edit_shared_by(receipt)

        elif choice == "c":
            return

        else:
            print("Please enter e or c.")


# --------------------------------------------------------------------------------------
# Extra charges
# --------------------------------------------------------------------------------------    

def wants_extra_charges() -> bool:
    return get_validated_input(
        "Would you like to add an extra charge (y/n)? ",
        validation.validate_yes_no,
    )


def get_charge_type() -> int:
    return get_validated_input(
        "Choose charge type: 1. service charge, 2. other (percentage or fixed): ",
        validation.validate_num_option,
        2,
    )


def add_service_charge(receipt: Receipt) -> None:
    # get valid service charge percentage and add to receipt
    receipt.service_rate = get_validated_input(
        "Please enter a percentage for the service charge: ",
        validation.validate_percentage_charge
    )


def add_other_charges(receipt: Receipt) -> None:
    while True:
        # choose percentage or fixed
        other_charge_type = get_validated_input(
            "Choose 1. a percentage charge (unequally split), or 2. a fixed charge (equally split): ",
            validation.validate_num_option,
            2,
        )

        refresh_receipt(receipt)

        # get charge value
        if other_charge_type == 1:
            prompt = "Please enter a percentage for the extra charge: "
            validator = validation.validate_percentage_charge
            charge_kind = ChargeType.PERCENTAGE
        elif other_charge_type == 2:
            prompt = "Please enter the amount for the extra charge: "
            validator = validation.validate_fixed_charge
            charge_kind = ChargeType.FIXED

        other_charge_value = get_validated_input(prompt, validator)

        # store charge in receipt
        receipt.extra_charges.append(
            Charge(charge_kind, other_charge_value)
        )

        refresh_receipt(receipt)

        # ask whether to add another
        another = get_validated_input(
            "Would you like to add another charge? (y/n): ",
            validation.validate_yes_no,
        )

        if not another:
            break


def add_extra_charges(receipt: Receipt) -> None:
    refresh_receipt(receipt)

    if not wants_extra_charges():
        return

    charge_type = get_charge_type()

    refresh_receipt(receipt)

    if charge_type == 1:  # standard service charge
        add_service_charge(receipt)

    elif charge_type == 2:  # other charge
        add_other_charges(receipt)


# --------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------    
def main():
    clear_screen()

    try:
        receipt = Receipt()

        display_start_menu()
    
        get_people(receipt)
        get_items(receipt)
        assign_items(receipt)
    
        split_cost(receipt)

        add_extra_charges(receipt)
        apply_extra_charges(receipt)
    
        apply_rounding(receipt)

        clear_screen()
        show_receipt(receipt)
        show_amount_owed(receipt)
        print("\nThank you for using Receipt Splitter!\nCome back next time!\n")

    except KeyboardInterrupt:
        clear_screen()
        print("\nGoodbye!")
        time.sleep(2)
        clear_screen()


if __name__ == "__main__":
    main()