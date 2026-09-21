"""Command-line interface for the receipt splitter."""

import time
from decimal import Decimal

from prompt_toolkit import PromptSession
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit import print_formatted_text
from prompt_toolkit.formatted_text import HTML

from . import validation
from .calculator import apply_extra_charges, apply_rounding, split_cost
from .formatter import ReceiptFormat, format_amount_owed, format_receipt, show_amount_owed, show_receipt
from .models import Charge, ChargeType, Receipt, Share, find_key_ci
from .export import next_receipt_path, prompt_save_with_timeout, prompt_save_or_continue, receipt_to_png


kb = KeyBindings()


@kb.add("escape")
def _(event):
    event.app.exit(exception=KeyboardInterrupt)


session = PromptSession()


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
            clear_line()
            if error:
                clear_lines(2)
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


def display_header(title: str, match_receipt: bool = False) -> None:
    title_width = len(title)
    receipt_width = ReceiptFormat.line_width

    if not match_receipt:
        print(f"\n{title}")
        print("─" * title_width + "\n")
    else:
        print("\n" + title.center(receipt_width))
        print("─" * receipt_width + "\n")


def display_start_menu() -> str:
    display_header("~~* RECEIPT SPLITTER *~~")
    print("Split your bill, fairly.\n")
    print("Press Enter to start.")
    print("Enter 'f' for Fast Split mode!")
    print("Press Esc anytime to quit.\n")

    menu_choice = get_input("")

    return menu_choice


def refresh_receipt(receipt: Receipt) -> None:
    clear_screen()
    display_header("~~* RECEIPT SPLITTER *~~", match_receipt=True)
    show_receipt(receipt)
    print()
    print()


# ======================================================================================
### FAST SPLIT ###
# ======================================================================================

def fast_split(receipt: Receipt) -> None:
    while True:
        clear_screen()
        display_header("~~* RECEIPT SPLITTER · FAST SPLIT *~~", match_receipt=True)
        show_receipt(receipt)

        print_formatted_text(
            HTML(
                "\n\n↓ Add e.g."
                "<color fg='#56B6C2'> pizza, 10, alice, bob </color>"
                "/<color fg='#E5C07B'> Enter </color>when done\n"
            )
        )

        details = get_validated_input(
            "> ",
            validation.validate_fast_split_line,
            receipt.items,
        )

        if details == []:
            break

        item_name, item_price, *shared_names = details

        for name in shared_names:
            if not find_key_ci(receipt.people, name):
                receipt.add_person(name)

        receipt.add_item(item_name, item_price)

        shared_details = [
            Share(find_key_ci(receipt.people, name), None) 
            for name in shared_names
        ]
        receipt.items[item_name].shared_by = shared_details

    clear_screen()
    display_header("~~* RECEIPT SPLITTER · FAST SPLIT *~~", match_receipt=True)
    show_receipt(receipt)

    print_formatted_text(
        HTML(
            "\n\n↓ Extra charges? "
            "e.g.<color fg='#56B6C2'> 2, 10% tax, 5% </color>"
            "/<color fg='#E5C07B'> Enter </color>if none\n"
        )
    )

    clean_charges = get_validated_input(
        "> ",
        validation.validate_fast_split_extra_charges,
    )

    for charge, label in clean_charges:
        if charge.endswith("%"):
            receipt.extra_charges.append(
                Charge(
                    ChargeType.PERCENTAGE,
                    Decimal(charge.removesuffix("%")) / 100,
                    label,
                )
            )
        else:
            receipt.extra_charges.append(
                Charge(
                    ChargeType.FIXED,
                    Decimal(charge),
                    label,
                    )
                )

    split_cost(receipt)
    apply_extra_charges(receipt)
    apply_rounding(receipt)

    clear_screen()
    display_header("~~* RECEIPT SPLITTER · FAST SPLIT *~~", match_receipt=True)
    show_receipt(receipt)
    show_amount_owed(receipt)
    print()
    print()

    if prompt_save_with_timeout():
        clear_line()
        success, err = receipt_to_png(
            format_receipt(receipt) + "\n" + format_amount_owed(receipt),
            next_receipt_path(),
        )
        if success:
            print("✓ Saved!\n")
        else:
            print("✗ Could not save: " + err + "\n")
    else:
        clear_line()


# ======================================================================================
### NORMAL SPLIT ###
# ======================================================================================
# --------------------------------------------------------------------------------------
# People
# --------------------------------------------------------------------------------------


def display_people(receipt: Receipt) -> None:
    display_header("~~* RECEIPT SPLITTER *~~", match_receipt=True)
    display_header("PEOPLE")

    for i, person in enumerate(receipt.people.values(), 1):
        print(f"{i}. {person.name}")


def edit_person(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)
    print()

    person = choose_from_list(list(receipt.people.values()), "person to edit")

    if person == "0":
        return

    if person == -1:
        return -1

    new_name = get_validated_input(
        f"Enter new name for {person.name} (or 0 to go back): ",
        validation.validate_new_person_name,
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

    if person == "0":
        return

    if person == -1:
        return -1

    receipt.remove_person(person.name)


def add_person(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)
    print()

    name = get_validated_input(
        "Enter name for new person (or 0 to go back): ",
        validation.validate_new_person_name,
        receipt.people,
        allow_back=True,
    )

    if name == "0":
        return

    receipt.add_person(name)


def get_people(receipt: Receipt) -> None:
    clear_screen()
    display_people(receipt)

    print("↓ Add people (e.g. Alice, Bob)\n")

    names = get_validated_input(
        "> ",
        validation.validate_person_names,
    )

    for name in names:
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

        choice = get_input("> ").strip().lower()

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
                return

        else:
            input_error = True


# --------------------------------------------------------------------------------------
# Items
# --------------------------------------------------------------------------------------


def display_items(receipt: Receipt) -> None:
    display_header("~~* RECEIPT SPLITTER *~~", match_receipt=True)
    display_header("ITEMS")

    for i, item in enumerate(receipt.items.values(), 1):
        print(f"{i}. {item.name} - £{item.price:.2f}")


def add_item(receipt: Receipt, allow_item_back: bool = False) -> None:
    clear_screen()
    display_items(receipt)

    if receipt.items:
        print()

    prompt = "↓ Add item (name, price)"

    if allow_item_back:
        prompt += " (or 0 to go back)"

    print(prompt + "\n")

    value = get_validated_input(
        "> ",
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

    if item == "0":
        return

    if item == -1:
        return -1

    new_name, new_price = get_validated_input(
        f"Enter new details for {item.name}: ",
        validation.validate_item,
        [n for n in receipt.items if n.lower() != item.name.lower()]
    )

    receipt.edit_item(item.name, new_name, new_price)


def delete_item(receipt: Receipt) -> None:
    clear_screen()
    display_items(receipt)
    print()

    item = choose_from_list(list(receipt.items.values()), "item to delete")

    if item == "0":
        return

    if item == -1:
        return -1

    receipt.remove_item(item.name)


def get_items(receipt: Receipt) -> None:
    add_item(receipt)

    clear_screen()
    display_items(receipt)
    print()

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

        choice = get_input("> ").strip().lower()

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

    shared_item = receipt.items[find_key_ci(receipt.items, name)]

    refresh_receipt(receipt)

    print(f'↓ Who shared {shared_item.name}? (e.g. Alice, Bob or "all")')

    for item in receipt.items.values():
        shared_names = get_validated_input(
            "> ",
            validation.validate_shared_names,
            receipt.people,
        )

    shared_item.shared_by = [
        Share(find_key_ci(receipt.people, name), None)
        for name in shared_names
    ]


def edit_item_shares(receipt: Receipt) -> bool:
    refresh_receipt(receipt)

    name = get_validated_input(
        "Enter item name to adjust shares (or 0 to go back): ",
        validation.validate_item_name,
        list(receipt.items),
        allow_back=True,
        need_existing=True,
    )

    if name == "0":
        return

    shared_item = receipt.items[find_key_ci(receipt.items, name)]

    if len(shared_item.shared_by) == 1:
        return False

    for i in range(len(shared_item.shared_by)):
        person_name = shared_item.shared_by[i].name
        s = get_validated_input(
            f"Enter shares for {person_name}: ",
            validation.validate_shares_input,
        )
        shared_item.shared_by[i] = Share(person_name, s)

        refresh_receipt(receipt)

    return True


def assign_items(receipt: Receipt) -> None:
    refresh_receipt(receipt)

    if len(receipt.people) == 1:
        person = next(iter(receipt.people))
        for item in receipt.items.values():  
            item.shared_by = [Share(person, None)]
        return

    for item in receipt.items.values():
        print(f'↓ Who shared {item.name}? (e.g. Alice, Bob or "all")\n')

        shared_names = get_validated_input(
            "> ",
            validation.validate_shared_names,
            receipt.people,
        )

        item.shared_by = [
            Share(find_key_ci(receipt.people, name), None)
            for name in shared_names
        ]

        refresh_receipt(receipt)

    input_error = False
    shares_error = False

    while True:
        refresh_receipt(receipt)

        print("[e] Edit who shared  [s] Add custom shares  [c] Continue")

        if input_error:
            print("\nPlease enter e, w or c.\n")
            input_error = False

        if shares_error:
            print("\nCustom shares aren't needed for items only shared by one person.\n")
            shares_error = False

        choice = get_input("> ").strip().lower()

        if choice == "e":
            edit_shared_by(receipt)

        elif choice == "s":
            if not edit_item_shares(receipt):
                shares_error = True

        elif choice == "c":
            return

        else:
            input_error = True


# --------------------------------------------------------------------------------------
# Extra charges
# --------------------------------------------------------------------------------------


def add_extra_charges(receipt: Receipt) -> None:
    while True:
        refresh_receipt(receipt)

        print("Would you like to add an extra charge?\n\n"
            "1. Service charge\n2. Custom percentage charge\n"
            "3. Custom fixed charge\n4. No extra charge\n")

        charge_type = get_validated_input(
            "> ",
            validation.validate_num_option,
            4,
        )

        refresh_receipt(receipt)

        if charge_type == 1:
            if receipt.service_rate != 0:
                override_choice = get_validated_input(
                    "Would you like to 1. override or 2. keep the existing service charge?",
                    validation.validate_num_option,
                    2,
                )

                if override_choice == 2:
                    continue

            refresh_receipt(receipt)

            service_rate, _ = get_validated_input(
                "Please enter the service charge percentage: ",
                validation.validate_percentage_charge,
            )

            receipt.service_rate = service_rate

        elif charge_type == 4:
            return

        else:
            if charge_type == 2:
                prompt = "Please enter the percentage charge (e.g. 10 or 10 tax): "
                validator = validation.validate_percentage_charge
                charge_kind = ChargeType.PERCENTAGE
            else:
                prompt = "Please enter the extra charge amount (e.g. 5 or 5 tip): "
                validator = validation.validate_fixed_charge
                charge_kind = ChargeType.FIXED

            charge_value, charge_label = get_validated_input(prompt, validator)

            receipt.extra_charges.append(Charge(charge_kind, charge_value, charge_label))


# --------------------------------------------------------------------------------------
# Saving
# --------------------------------------------------------------------------------------


def save_receipt(receipt) -> None:
    output_dir = next_receipt_path()
    if prompt_save_or_continue():
        success, err = receipt_to_png(
            format_receipt(receipt) + "\n" + format_amount_owed(receipt),
            next_receipt_path(),
        )
        clear_line()
        if success:
            print(f"✓ Saved to {output_dir}\n")
        else:
            print("✗ Could not save: " + err + "\n")
    else:
        clear_line()

# --------------------------------------------------------------------------------------
# MAIN
# --------------------------------------------------------------------------------------
def main():
    clear_screen()

    try:
        receipt = Receipt()

        menu_choice = display_start_menu()
        if menu_choice.strip().lower() == "f":
            fast_split(receipt)
            return

        get_people(receipt)
        get_items(receipt)
        assign_items(receipt)

        split_cost(receipt)
        add_extra_charges(receipt)
        apply_extra_charges(receipt)
        apply_rounding(receipt)

        clear_screen()
        display_header("~~* RECEIPT SPLITTER *~~", match_receipt=True)
        show_receipt(receipt)
        show_amount_owed(receipt)
        print()
        print()

        save_receipt(receipt)

        print("Thank you for using Receipt Splitter!\nCome back next time!\n")

    except KeyboardInterrupt:
        clear_screen()
        print("\nGoodbye!")
        time.sleep(2)
        clear_screen()


if __name__ == "__main__":
    main()
