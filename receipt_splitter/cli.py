"""Command-line interface for the receipt splitter."""

from .calculator import split_cost, apply_extra_charges, apply_rounding
from . import validation
from .models import Receipt
from .formatter import show_receipt

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


def get_people(receipt: Receipt) -> None:
    # validate number of people
    while True:
        try:
            num_people = validation.validate_num_people(get_input("How many people? "))
            clear_line()
            break
        except ValueError as e:
            print(e)

    
    # get each person's name and validate
    display_header("People")

    for i in range(num_people):
        while True:
            try:
                name = validation.validate_person_name(
                    get_input(f"Person {i+1}: "), receipt.people
                )
                break
            except ValueError as e:
                print(e)

        receipt.add_person(name)


def get_items(receipt: Receipt) -> None:
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
 
            
        # print to visible list of items
        print(f"Item {count + 1}: {name}, {price}")

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
            return


def assign_items(receipt: Receipt) -> None:
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


def get_extra_charges(receipt: Receipt) -> None:
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

    except KeyboardInterrupt:
        print("\nGoodbye!")
        time.sleep(2)
        clear_screen()


if __name__ == "__main__":
    main()