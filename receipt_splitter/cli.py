"""Command-line interface for the receipt splitter."""

from decimal import Decimal, InvalidOperation
from .calculator import split_cost, apply_extra_charges, apply_rounding, calculate_subtotal, calculate_receipt_total, calculate_people_total
from . import validation
from .models import Receipt
from .formatter import show_receipt


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