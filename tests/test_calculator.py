from decimal import Decimal

from receipt_splitter.calculator import (
    apply_extra_charges,
    calculate_people_total,
    calculate_receipt_total,
    calculate_subtotal,
    split_cost,
)
from receipt_splitter.models import Share


def test_calculate_subtotal(sample_receipt):
    assert calculate_subtotal(sample_receipt) == Decimal("30.00")


def test_calculate_receipt_total(sample_receipt):
    assert calculate_receipt_total(sample_receipt) == Decimal("36.50")


def test_split_cost(sample_receipt):
    split_cost(sample_receipt)

    assert sample_receipt.people["Alice"].total == Decimal("20.00")
    assert sample_receipt.people["Bob"].total == Decimal("10.00")


def test_split_cost_with_shares(sample_receipt):
    sample_receipt.items["Pizza"].shared_by = [
        Share("Alice", Decimal("1")),
        Share("Bob", Decimal("3")),
    ]

    split_cost(sample_receipt)

    assert sample_receipt.people["Alice"].total == Decimal("15.00")
    assert sample_receipt.people["Bob"].total == Decimal("15.00")


def test_calculate_people_total(sample_receipt):
    assert calculate_people_total(sample_receipt) == Decimal(0)


def test_calculate_people_total_after_split(sample_receipt):
    split_cost(sample_receipt)

    assert calculate_people_total(sample_receipt) == Decimal("30.00")


def test_apply_extra_charges(sample_receipt):
    split_cost(sample_receipt)
    apply_extra_charges(sample_receipt)

    assert sample_receipt.people["Alice"].total == Decimal("24.00")
    assert sample_receipt.people["Bob"].total == Decimal("12.50")
