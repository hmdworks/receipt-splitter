print("CLI FILE IS RUNNING")
from decimal import Decimal, InvalidOperation
from .calculator import split_cost, apply_rounding


def get_people():
    people = {}

    # validate number of people
    while True:
        try:
            num_people = int(input("How many people? ").strip())

            if num_people <= 0:
                print("There must be at least one person.")
                continue

            break

        except ValueError:
            print("Please enter a whole number.")

    # get each person's name
    for i in range(num_people):
        while True:
            name = input(f"Person {i+1}: ").strip()

            # check for empty name
            if not name:
                print("Name cannot be empty.")
                continue

            # check for duplicate name
            if name in people:
                print("That person has already been added.")
                continue

            break

        people[name] = Decimal("0")

    return people


def get_items():
    items = {}
    count = 0

    while True: 
        # input validation loop
        while True:
            item_input = input(f"Add item {count + 1} (name, price): "
            ).strip()

            # check for comma
            if "," not in item_input:
                print("Please enter the item in the format: name, price (comma-separated).")
                continue

            item, price = item_input.split(",", 1)

            item = item.strip()
            price = price.strip()

            # check item name
            if not item:
                print("You must include an item name.")
                continue

            # check for duplicate item
            if item in items:
                print("That item has already been added.")
                continue

            # check price
            try:
                price = Decimal(price)
            except InvalidOperation:
                print("Price must be a valid number.")
                continue

            # check price positive
            if price <= 0:
                print("Price must be greater than 0.")
                continue

            # everything valid
            break

        # add price to items
        items[item] = price
        count += 1

        # ask to add another item
        while True:
            add_item = input("Add another item? (y/n): ").strip().lower()

            if add_item in ("y", "n"):
                break

            print("Please enter y or n.")

        if add_item == "n":
            return items


def assign_items(people, items):
    shared_by = {}

    # ask who shared each item
    for item in items:
        while True:
            shared = input(f"Who shared {item}? (comma-separated): ")

            names = [name.strip() for name in shared.split(",")]

            # check if any empty names
            if any(not name for name in names):
                print("Please enter valid names separated by commas.")
                continue

            # check if name exists
            if any(name not in people for name in names):
                print("Please only enter names that exist.")
                continue

            # check for and reject duplicate names
            if len(names) != len(set(names)):
                print("Please don't enter the same person more than once.")
                continue

            # add names for each item
            shared_by[item] = names
            break

    return shared_by


def add_extra_charges(people):
    service_rate = Decimal("0")

    # ask if service charge and validate y/n
    while True:
        service = input("Would you like to add a service charge? (y/n): ").strip().lower()

        if service in ("y", "n"):
            break

        print("Please enter y or n.")

    # validate percentage
    if service == "y":
        while True:
            service_input = input("Please enter a percentage for the service charge: ")

            try:
                service_rate = Decimal(service_input) / 100
            except InvalidOperation:
                print("Please enter a valid number.")
                continue

            if service_rate < 0:
                print("Service charge cannot be negative.")
                continue

            break

        # apply service charge
        for name in people:
            people[name] *= (1 + service_rate)

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

    service_rate = add_extra_charges(people) 
    
    apply_rounding(people)

    show_receipt(people, items, shared_by, service_rate)


if __name__ == "__main__":
    main()