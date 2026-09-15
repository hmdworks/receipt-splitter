from decimal import Decimal

import pytest

from receipt_splitter.calculator import apply_rounding
from receipt_splitter.models import Person, Receipt, ReceiptItem


@pytest.mark.parametrize(
    "total_amount, num_people, expected_totals",
    [
        (
            Decimal("10.00"),
            2,
            [Decimal("5.00"), Decimal("5.00")],
        ),
        (
            Decimal("10.00"),
            3,
            [Decimal("3.34"), Decimal("3.33"), Decimal("3.33")],
        ),
        (
            Decimal("10.00"),
            7,
            [Decimal("1.43"), Decimal("1.43"), Decimal("1.43"),
            Decimal("1.43"), Decimal("1.43"), Decimal("1.43"),
            Decimal("1.42"),
            ],
        ),
    ],
)
def test_apply_rounding_exact_order(total_amount, num_people, expected_totals):
    raw_share = total_amount / Decimal(num_people)
    names = [f"Person_{i}" for i in range(num_people)]

    receipt = Receipt(
        items={"item": ReceiptItem(name="Item", price=total_amount, shared_by=names)},
        people={name: Person(name=name, total=raw_share) for name in names},
    )

    apply_rounding(receipt)

    actual_totals = [p.total for p in receipt.people.values()]

    assert actual_totals == expected_totals