"""Command-line interface for the receipt splitter."""

import time

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings

from . import validation
from .calculator import apply_extra_charges, apply_rounding, split_cost
from .formatter import show_amount_owed, show_receipt
from .models import Charge, ChargeType, Receipt, find_key_ci

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


# returns user input and listens for Esc
def get_input(prompt: str) -> str:
    while True:
        try:
            return session.prompt(prompt, key_bindings=kb)
        except KeyboardInterrupt:
            if confirm_exit():
                raise

            clear_lines(3)


def get_validated_input(prompt, validator, *args, allow_back: bool = False, **kwargs):
    """Validates user input with appropriate validator.
    Can 'allow back' (return if user input is "0").
    Clears prompts and errors with ANSI codes in helper fns."""

    error = False
    while True:
        user_input = get_input(prompt)

        if allow_back and user_input == "0":
            return user_input

        try:
            value = validator(user_input, *args, **kwargs)
            clear_line()
            return value
        except ValueError as e:
            clear_line()  # clear prompt
            if error:
                clear_lines(2)  # clear previous error plus blank line
            print(e)
            print()
            error = True


def choose_from_list(options, action: str):
    if not options:
        return -1

    choice = get_validated_input(
        f"Enter number for {action} (or 0 to go back): ",
        validation.validate_num_option,
        len(options),
        allow_back=True,
    )

    if choice == "0":
        return "0"

    return options[choice - 1]


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
    print()

    person = choose_from_list(list(receipt.people.values()), "person to edit")

    if person == "0":  # user chose to go back
        return

    if person == -1:  # no person to edit
        return -1

    new_name = get_validated_input(
        f"Enter new name for {person.name} (or 0 to go back): ",
        validation.validate_person_name,
        [n for n in receipt.people if n.lower() != person.name.lower()],
        allow_back=True,
    )

    if new_name == "0":
        return

    receipt.rename_person(person.name, new_name)


def delete_person(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)
    print()

    person = choose_from_list(list(receipt.people.values()), "person to delete")

    if person == "0":  # user chose to go back
        return

    if person == -1:  # no person to delete
        return -1

    receipt.remove_person(person.name)


def add_person(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)
    print()

    name = get_validated_input(
        "Enter name for new person (or 0 to go back): ",
        validation.validate_person_name,
        receipt.people,
        allow_back=True,
    )

    if name == "0":
        return

    receipt.add_person(name)


def get_people(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)

    num_people = get_validated_input(
        "How many people? ",
        validation.validate_num_people,
    )

    clear_screen()
    display_people(receipt)

    for i in range(num_people):
        name = get_validated_input(
            f"Person {i + 1}: ", validation.validate_person_name, receipt.people
        )

        receipt.add_person(name)

    input_error = False
    empty = False
    no_options = False

    while True:
        clear_screen()
        display_people(receipt)
        print("\n[a] Add  [e] Edit  [d] Delete  [c] Continue")

        if input_error:
            print("\nPlease enter a, e, d, or c.\n")
            input_error = False

        if empty:
            print("\nYou must include at least one person.\n")
            empty = False

        if no_options:
            print(
                "\nThere are no options to choose from. Please add before editing or deleting.\n"
            )
            no_options = False

        choice = get_input("> ").lower()

        if choice == "a":
            add_person(receipt)

        elif choice == "e":
            if edit_person(receipt) == -1:
                no_options = True

        elif choice == "d":
            if delete_person(receipt) == -1:
                no_options = True

        elif choice == "c":
            if not receipt.people:
                empty = True
            else:
                clear_screen()
                display_people(receipt)
                print()

                confirmed = get_validated_input(
                    "You won't be able to edit people after this. Continue? (y/n): ",
                    validation.validate_yes_no,
                )
                if confirmed:
                    return
        else:
            input_error = True


# --------------------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------------------


def display_items(receipt: Receipt) -> None:
    display_header("Items")

    for i, item in enumerate(receipt.items.values(), 1):
        print(f"{i}. {item.name} - £{item.price:.2f}")


def add_item(receipt: Receipt, allow_item_back: bool = False) -> None:
    clear_screen()
    display_items(receipt)

    if receipt.items:
        print()

    prompt = "Add item (name, price)"

    if allow_item_back:
        prompt += " (or 0 to go back)"

    value = get_validated_input(
        f"{prompt}: ",
        validation.validate_item,
        receipt.items,
        allow_back=allow_item_back,
    )

    if value == "0":
        return

    name, price = value

    receipt.add_item(name, price)


def edit_item(receipt: Receipt) -> None:
    clear_screen()
    display_items(receipt)
    print()

    item = choose_from_list(list(receipt.items.values()), "item to edit")

    if item == "0":  # user chose to go back
        return

    if item == -1:  # no item to edit
        return -1

    if get_validated_input(
        f"Change item name? (current: {item.name}) (y/n): ",
        validation.validate_yes_no,
    ):
        new_name = get_validated_input(
            "Enter new name: ",
            validation.validate_item_name,
            [n for n in receipt.items if n.lower() != item.name.lower()],
            need_existing=False,
        )
    else:
        new_name = item.name

    if get_validated_input(
        f"Change price? (current: {item.price:.2f}) (y/n): ",
        validation.validate_yes_no,
    ):
        new_price = get_validated_input(
            "Enter new price: ",
            validation.validate_price,
        )
    else:
        new_price = item.price

    receipt.edit_item(
        item.name,
        new_name,
        new_price,
    )


def delete_item(receipt: Receipt) -> None:
    clear_screen()
    display_items(receipt)
    print()

    item = choose_from_list(list(receipt.items.values()), "item to delete")

    if item == "0":  # user chose to go back
        return

    if item == -1:  # no item to delete
        return -1

    receipt.remove_item(item.name)


def get_items(receipt: Receipt) -> None:
    while True:
        add_item(receipt)

        clear_screen()
        display_items(receipt)
        print()

        another = get_validated_input(
            "Add another item? (y/n): ", validation.validate_yes_no
        )

        if not another:
            break

    input_error = False
    empty = False
    no_options = False

    while True:
        clear_screen()
        display_items(receipt)

        print("\n[a] Add  [e] Edit  [d] Delete  [c] Continue")

        if input_error:
            print("\nPlease enter a, e, d, or c.\n")
            input_error = False

        if empty:
            print("\nYou must add at least one item.\n")
            empty = False

        if no_options:
            print(
                "\nThere are no options to choose from. Please add before editing or deleting.\n"
            )
            no_options = False

        choice = get_input("> ").lower()

        if choice == "a":
            add_item(receipt, allow_item_back=True)

        elif choice == "e":
            if edit_item(receipt) == -1:
                no_options = True

        elif choice == "d":
            if delete_item(receipt) == -1:
                no_options = True

        elif choice == "c":
            if not receipt.items:
                empty = True
            else:
                clear_screen()
                display_items(receipt)
                print()

                confirmed = get_validated_input(
                    "You won't be able to edit items after this. Continue? (y/n): ",
                    validation.validate_yes_no,
                )
                if confirmed:
                    return

        else:
            input_error = True


# --------------------------------------------------------------------------------------
# Shared items
# --------------------------------------------------------------------------------------


def edit_shared_by(receipt: Receipt) -> None:
    refresh_receipt(receipt)

    name = get_validated_input(
        "Enter item name to edit (or 0 to go back): ",
        validation.validate_item_name,
        list(receipt.items),
        allow_back=True,
        need_existing=True,
    )

    if name == "0":
        return

    for item in receipt.items.values():
        if item.name.lower() == name.lower():
            shared_item = item
            break

    refresh_receipt(receipt)

    shared_names = get_validated_input(
        f'Who shared {shared_item.name}? (e.g. Alice, Bob or "all"): ',
        validation.validate_shared_names,
        receipt.people,
    )

    shared_item.shared_by = [find_key_ci(receipt.people, name) for name in shared_names]


def assign_items(receipt: Receipt) -> None:
    refresh_receipt(receipt)

    for item in receipt.items.values():
        shared_names = get_validated_input(
            f'Who shared {item.name}? (e.g. Alice, Bob or "all"): ',
            validation.validate_shared_names,
            receipt.people,
        )

        item.shared_by = [find_key_ci(receipt.people, name) for name in shared_names]

        refresh_receipt(receipt)

    input_error = False

    while True:
        refresh_receipt(receipt)

        print("[e] Edit  [c] Continue")

        if input_error:
            print("\nPlease enter e or c.\n")
            input_error = False

        choice = get_input("> ").lower()

        if choice == "e":
            edit_shared_by(receipt)

        elif choice == "c":
            return

        else:
            input_error = True


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
        "Choose: 1. standard service charge, or 2. other (percentage/fixed): ",
        validation.validate_num_option,
        2,
    )


def add_service_charge(receipt: Receipt) -> None:
    receipt.service_rate = get_validated_input(
        "Please enter the service charge percentage: ",
        validation.validate_percentage_charge,
    )


def add_other_charges(receipt: Receipt) -> None:
    while True:
        other_charge_type = get_validated_input(
            "Choose: 1. percentage charge (unequal split), or 2. fixed charge (equal split): ",
            validation.validate_num_option,
            2,
        )

        refresh_receipt(receipt)

        if other_charge_type == 1:
            prompt = "Please enter the extra charge percentage: "
            validator = validation.validate_percentage_charge
            charge_kind = ChargeType.PERCENTAGE
        elif other_charge_type == 2:
            prompt = "Please enter the extra charge amount: "
            validator = validation.validate_fixed_charge
            charge_kind = ChargeType.FIXED

        other_charge_value = get_validated_input(prompt, validator)

        receipt.extra_charges.append(Charge(charge_kind, other_charge_value))

        refresh_receipt(receipt)

        if not wants_extra_charges():
            break


def add_extra_charges(receipt: Receipt) -> None:
    refresh_receipt(receipt)

    if not wants_extra_charges():
        return

    charge_type = get_charge_type()

    refresh_receipt(receipt)

    if charge_type == 1:  # standard service charge
        add_service_charge(receipt)

        refresh_receipt(receipt)

        if wants_extra_charges():  # ask if another charge is needed
            add_other_charges(receipt)

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
