"""Calculation logic for the receipt splitter."""

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from .models import Receipt


def calculate_subtotal(receipt: Receipt) -> Decimal:
    return sum(item.price for item in receipt.items.values())


def calculate_receipt_total(receipt: Receipt) -> Decimal:
    subtotal = calculate_subtotal(receipt)
    return subtotal * (1 + receipt.service_rate)


def calculate_people_total(receipt: Receipt) -> Decimal:
    return sum(person.total for person in receipt.people.values())



def split_cost(receipt: Receipt) -> None:
    for item in receipt.items.values():
        # work out share and add to person's total
        share = item.price / len(item.shared_by)
        for name in item.shared_by:
            receipt.people[name].total += share


def apply_extra_charges(receipt: Receipt) -> None:
    # apply service charge
    for person in receipt.people.values():
        person.total *= (1 + receipt.service_rate)



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
    # round everyone down to the nearest penny
    rounded = {
        name: _round_down_to_penny(person.total)
        for name, person in receipt.people.items()
    }

    # round the receipt total to the nearest penny
    target_total = _round_half_up_to_penny(calculate_receipt_total(receipt))

    # work out how much left to distribute in pennies
    rounded_total = sum(rounded.values())
    difference = target_total - rounded_total
    pennies = int(difference * 100)

    # work out who had the largest fractional remainder, then hand out
    # pennies in that order
    remainders = {
        name: receipt.people[name].total - rounded[name]
        for name in receipt.people
        }
    _distribute_pennies(rounded, remainders, pennies)

    # update people with final amounts
    for name, person in receipt.people.items():
        person.total = rounded[name]