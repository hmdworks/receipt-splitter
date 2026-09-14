"""Calculation logic for the receipt splitter."""

from decimal import ROUND_DOWN, ROUND_HALF_UP, Decimal

from .models import ChargeType, Receipt


def calculate_subtotal(receipt: Receipt) -> Decimal:
    return sum(item.price for item in receipt.items.values())


def calculate_receipt_total(receipt: Receipt) -> Decimal:
    subtotal = calculate_subtotal(receipt)

    total = subtotal * (1 + receipt.service_rate)

    for charge in receipt.extra_charges:
        if charge.type == ChargeType.PERCENTAGE:
            total += subtotal * charge.value
        elif charge.type == ChargeType.FIXED:
            total += charge.value

    return total


def calculate_people_total(receipt: Receipt) -> Decimal:
    return sum(person.total for person in receipt.people.values())


def split_cost(receipt: Receipt) -> None:
    for item in receipt.items.values():
        share = item.price / len(item.shared_by)
        for name in item.shared_by:
            receipt.people[name].total += share


def apply_extra_charges(receipt: Receipt) -> None:
    for person in receipt.people.values():
        extra_charges = Decimal(0)

        for charge in receipt.extra_charges:
            if charge.type == ChargeType.PERCENTAGE:
                extra_charges += person.total * charge.value
            elif charge.type == ChargeType.FIXED:
                extra_charges += charge.value / len(receipt.people)

        person.total *= 1 + receipt.service_rate
        person.total += extra_charges


def _round_down_to_penny(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_DOWN)


def _round_half_up_to_penny(amount: Decimal) -> Decimal:
    return amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def _distribute_pennies(rounded: dict, remainders: dict, pennies: int) -> None:
    """Hand out extra pennies, one at a time, to whoever has the
    largest leftover fractional remainder. Loops back through the list if
    there are more pennies than people."""
    order = sorted(remainders, key=remainders.get, reverse=True)

    for i in range(pennies):
        name = order[i % len(order)]
        rounded[name] += Decimal("0.01")


def apply_rounding(receipt: Receipt):
    """Rounds everyone down to the nearest penny, and receipt total to nearest penny.
    Then distributes remaining pennies based on largest fractional remainder.
    If tied, distributes in order on receipt."""
    rounded = {
        name: _round_down_to_penny(person.total)
        for name, person in receipt.people.items()
    }

    target_total = _round_half_up_to_penny(calculate_receipt_total(receipt))

    rounded_total = sum(rounded.values())
    difference = target_total - rounded_total
    pennies = int(difference * 100)

    remainders = {
        name: receipt.people[name].total - rounded[name] for name in receipt.people
    }
    _distribute_pennies(rounded, remainders, pennies)

    for name, person in receipt.people.items():
        person.total = rounded[name]
