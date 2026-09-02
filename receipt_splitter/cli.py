"""Command-line interface for the receipt splitter."""

from .calculator import split_cost, apply_extra_charges, apply_rounding
from . import validation
from .models import Receipt
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


def get_input(prompt: str) -> str:
    return session.prompt(prompt, key_bindings=kb)


# ANSI codes to clear inputs
def clear_line() -> None:
    print("\033[1A\033[2K", end="")


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

    while True:
        try:
            new_name = validation.validate_person_name(
                get_input(f"New name [{person.name}]: "),
                receipt.people,
            )
            break
        except ValueError as e:
            print(e)

    receipt.rename_person(person.name, new_name)


def delete_person(receipt: Receipt) -> None:
    clear_screen()
    people = list(receipt.people.values())

    display_people(receipt)

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
    while True:
        try:
            name = validation.validate_person_name(
                get_input("Name: "),
                receipt.people,
            )
            break
        except ValueError as e:
            print(e)

    receipt.add_person(name)


def get_people(receipt: Receipt) -> None:
    clear_screen()
    display_header("People")

    # validate number of people
    while True:
        try:
            num_people = validation.validate_num_people(get_input("How many people? "))
            clear_line()
            break
        except ValueError as e:
            print(e)

    
    # get each person's name and validate
    for i in range(num_people):
        while True:
            try:
                name = validation.validate_person_name(
                    get_input(f"Person {i+1}: "), receipt.people
                )
                clear_line()
                break
            except ValueError as e:
                print(e)

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

    while True:
        try:
            raw_name, raw_price = validation.validate_item_line(
                get_input("\nAdd item (name, price): ")
            )
            name = validation.validate_item_name(
                raw_name,
                receipt.items,
            )
            price = validation.validate_price(raw_price)
            clear_line()
            break
        except ValueError as e:
            print(e)

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
    clear_screen()
    display_header("Items")

    count = 0

    while True:
        # validate input
        while True:
            try:
                raw_name, raw_price = validation.validate_item_line(
                    get_input(f"Add item {count + 1} (name, price): ")
                )
                name = validation.validate_item_name(raw_name, receipt.items)
                price = validation.validate_price(raw_price)
                clear_line()
                break
            except ValueError as e:
                print(e)

        receipt.add_item(name, price)
        count += 1

        # ask to add another item
        while True:
            try:
                add_another = validation.validate_yes_no(
                    get_input("Add another item? (y/n): ")
                )
                clear_line()
                break
            except ValueError as e:
                print(e)

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
    clear_screen()
    show_receipt(receipt)
    
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

    while True:
        try:
            names = validation.validate_shared_names(
                get_input(
                    f"Who shared {item.name}? (comma-separated): "
                ),
                receipt.people,
            )
            break
        except ValueError as e:
            print(e)

    item.shared_by = names

    
def assign_items(receipt: Receipt) -> None:
    clear_screen()
    show_receipt(receipt)
    print()
    display_people(receipt)
    print()

    # ask who shared each item
    for item in receipt.items.values():
        while True:
            try:
                names = validation.validate_shared_names(
                    get_input(f"Who shared {item.name}? (comma-separated): "),
                    receipt.people,
                )
                clear_line()
                break
            except ValueError as e:
                print(e)

        item.shared_by = names
        clear_screen()
        show_receipt(receipt)
        print()
        display_people(receipt)
        print()
            

    while True:
        clear_screen()
        show_receipt(receipt)

        print("\n[e] Edit  [c] Continue")

        choice = get_input("> ").lower()

        if choice == "e":
            edit_shared_by(receipt)

        elif choice == "c":
            return

        else:
            print("Please enter e or c.")

            
def get_extra_charges(receipt: Receipt) -> None:
    clear_screen()
    show_receipt(receipt)
    print()

    # ask if service charge and validate y/n
    while True:
        try:
            wants_service = validation.validate_yes_no(
                get_input("Would you like to add a service charge? (y/n): ")
            )
            clear_line()
            break
        except ValueError as e:
            print(e)
 
    if not wants_service:
        return

    # get and validate percentage
    while True:
        try:
            receipt.service_rate = validation.validate_service_rate(
                get_input("Please enter a percentage for the service charge: ")
            )
            clear_line()
            break
        except ValueError as e:
            print(e)


def main():
    clear_screen()

    try:
        receipt = Receipt()

        display_start_menu()
    
        get_people(receipt)
        get_items(receipt)
        assign_items(receipt)
    
        split_cost(receipt)

        get_extra_charges(receipt)
        apply_extra_charges(receipt)
    
        apply_rounding(receipt)

        clear_screen()
        show_receipt(receipt)
        show_amount_owed(receipt)

    except KeyboardInterrupt:
        print("\nGoodbye!")
        time.sleep(2)
        clear_screen()


if __name__ == "__main__":
    main()