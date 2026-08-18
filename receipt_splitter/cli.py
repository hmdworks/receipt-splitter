"""Command-line interface for the receipt splitter."""

from decimal import Decimal, InvalidOperation
from .calculator import split_cost, apply_extra_charges, apply_rounding
from . import validation

def get_people():
    people = {}

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
                    input(f"Person {i+1}: "), people
                )
                break
            except ValueError as e:
                print(e)

        people[name] = Decimal("0")

    return people


def get_items():
    items = {}
    count = 0

    while True: 
        # input validation loop
        while True:
            try:
                raw_name, raw_price = validation.validate_item_line(
                    input(f"Add item {count + 1} (name, price): ")
                )
                item = validation.validate_item_name(raw_name, items)
                price = validation.validate_price(raw_price)
                break
            except ValueError as e:
                print(e)

        # add price to items
        items[item] = price
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
            return items


def assign_items(people, items):
    shared_by = {}

    # ask who shared each item
    for item in items:
        while True:
            try:
                names = validation.validate_shared_names(
                    input(f"Who shared {item}? (comma-separated): "),
                    people,
                )
                break
            except ValueError as e:
                print(e)
        
        # add names for each item
        shared_by[item] = names

    return shared_by


def get_extra_charges():
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
        return Decimal("0")

    # get and validate percentage
    while True:
        try:
            service_rate = validation.validate_service_rate(
                input("Please enter a percentage for the service charge: ")
            )
            break
        except ValueError as e:
            print(e)

    return service_rate


def show_receipt(people, items, shared_by, service_rate):
    # format receipt and embed values
    print("\n" + "=" * 40)
    print(" " * 17 + "RECEIPT")
    print("=" * 40)

    print("\nITEMS")
    print("-" * 40)

    subtotal = sum(items.values())

    for item, price in items.items():
        names = ", ".join(shared_by[item])
        print(f"{item:<25} £{price:>8.2f}")
        print(f"  Shared by: {names}")

    print("-" * 40)
    print(f"{'Subtotal':<25} £{subtotal:>8.2f}")

    if service_rate > 0:
        service_charge = subtotal * service_rate
        percentage = f"{service_rate * 100:.2f}".rstrip("0").rstrip(".")

        print(
            f"{f'Service charge ({percentage}%)':<25} "
            f"£{service_charge:>8.2f}"
        )

    total = subtotal * (1 + service_rate)

    print("-" * 40)
    print(f"{'Total':<25} £{total:>8.2f}")

    print("\n\nAMOUNT OWED")
    print("-" * 40)

    for name, amount in people.items():
        print(f"{name:<25} £{amount:>8.2f}")

    print("-" * 40)
    print(f"{'Total':<25} £{sum(people.values()):>8.2f}")
    print("=" * 40)


def main():
    people = get_people()

    items = get_items()

    shared_by = assign_items(people, items)
    
    split_cost(people, items, shared_by)

    service_rate = get_extra_charges() 

    apply_extra_charges(people, service_rate)

    apply_rounding(people)

    show_receipt(people, items, shared_by, service_rate)


if __name__ == "__main__":
    main()