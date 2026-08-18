"""Calculation logic for receipt splitter."""

from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

def split_cost(people, items, shared_by):
    for item, price in items.items():
        # work out cut and add to person's total
        cut = price / len(shared_by[item])
        for name in shared_by[item]:
            people[name] += cut


def apply_extra_charges(people, service_rate):
    # apply service charge
    for name in people:
        people[name] *= (1 + service_rate)


def apply_rounding(people):
    rounded = {}

    # round everyone down to the nearest penny
    for name, amount in people.items():
        rounded[name] = amount.quantize(
            Decimal("0.01"),
            rounding=ROUND_DOWN
        )
    # round the overall bill to the nearest penny
    total = sum(people.values())
    target_total = total.quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP
    )

    # work out how much left to distribute
    rounded_total = sum(rounded.values())
    difference = target_total - rounded_total

    # work out who had the largest fractional remainder
    remainders = {
        name: people[name] - rounded[name]
        for name in people
        }
    
    order = sorted(
        remainders, 
        key=remainders.get, 
        reverse=True
        )

    # distribute the leftover pennies in order of remainder
    pennies = int(difference * 100)

    for i in range(pennies):
        name = order[i % len(order)] # loop through people again if pennies > len(order)
        rounded[name] += Decimal("0.01")

    # update people with final amounts
    for name in people:
        people[name] = rounded[name]