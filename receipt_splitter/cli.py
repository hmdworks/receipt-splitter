"""Command-line interface for the receipt splitter."""

from decimal import Decimal, InvalidOperation
from .calculator import split_cost, apply_extra_charges, apply_rounding
from . import validation
from .models import Receipt


def get_people(receipt: Receipt) -> None:
    # validate number of people
    while True:
        try:
            num_people = validation.validate_num_people(input("How many people? "))
            break
        except ValueError as e:
            print(e)
    
    # get each person's name and validate
    for i in range(num_people):
        while True:
            try:
                name = validation.validate_person_name(
                    input(f"Person {i+1}: "), receipt.people
                )
                break
            except ValueError as e:
                print(e)

        receipt.add_person(name)


def get_items(receipt: Receipt) -> None:
    count = 0

    while True: 
        # validate input
        while True:
            try:
                raw_name, raw_price = validation.validate_item_line(
                    input(f"Add item {count + 1} (name, price): ")
                )
                name = validation.validate_item_name(raw_name, receipt.items)
                price = validation.validate_price(raw_price)
                break
            except ValueError as e:
                print(e)

        receipt.add_item(name, price)
        count += 1

        # ask to add another item
        while True:
            try:
                add_another = validation.validate_yes_no(
                    input("Add another item? (y/n): ")
                )
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
                    input(f"Who shared {item.name}? (comma-separated): "),
                    receipt.people,
                )
                break
            except ValueError as e:
                print(e)
        
        item.shared_by = names


def get_extra_charges(receipt: Receipt) -> None:
    # ask if service charge and validate y/n
    while True:
        try:
            wants_service = validation.validate_yes_no(
                input("Would you like to add a service charge? (y/n): ")
            )
            break
        except ValueError as e:
            print(e)
 
    if not wants_service:
        return

    # get and validate percentage
    while True:
        try:
            receipt.service_rate = validation.validate_service_rate(
                input("Please enter a percentage for the service charge: ")
            )
            break
        except ValueError as e:
            print(e)


def show_receipt(receipt: Receipt) -> None:
    print("\n" + "=" * 40)
    print(" " * 17 + "RECEIPT")
    print("=" * 40)

    print("\nITEMS")
    print("-" * 40)

    subtotal = sum(item.price for item in receipt.items.values())

    for item in receipt.items.values():
        names = ", ".join(item.shared_by)
        print(f"{item.name:<25} £{item.price:>8.2f}")
        print(f"  Shared by: {names}")

    print("-" * 40)
    print(f"{'Subtotal':<25} £{subtotal:>8.2f}")

    if receipt.service_rate > 0:
        service_charge = subtotal * receipt.service_rate
        percentage = f"{receipt.service_rate * 100:.2f}".rstrip("0").rstrip(".")

        print(
            f"{f'Service charge ({percentage}%)':<25} "
            f"£{service_charge:>8.2f}"
        )

    total = subtotal * (1 + receipt.service_rate)

    print("-" * 40)
    print(f"{'Total':<25} £{total:>8.2f}")

    print("\n\nAMOUNT OWED")
    print("-" * 40)

    for person in receipt.people.values():
        print(f"{person.name:<25} £{person.total:>8.2f}")

    print("-" * 40)
    print(f"{'Total':<25} £{sum(p.total for p in receipt.people.values()):>8.2f}")
    print("=" * 40)


def main():
    receipt = Receipt()
 
    get_people(receipt)
    get_items(receipt)
    assign_items(receipt)
 
    split_cost(receipt)
 
    get_extra_charges(receipt)
    apply_extra_charges(receipt)
 
    apply_rounding(receipt)
 
    show_receipt(receipt)


if __name__ == "__main__":
    main()