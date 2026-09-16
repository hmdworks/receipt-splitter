from decimal import Decimal

import pytest

from receipt_splitter.models import Charge, ChargeType, Receipt


@pytest.fixture
def sample_receipt():
    receipt = Receipt(
        service_rate=Decimal("0.10"),
        extra_charges=[
            Charge(ChargeType.PERCENTAGE, Decimal("0.05")),
            Charge(ChargeType.FIXED, Decimal("2.00")),
        ],
    )

    receipt.add_person("Alice")
    receipt.add_person("Bob")

    receipt.add_item("Pizza", Decimal("20.00"))
    receipt.add_item("Drinks", Decimal("10.00"))

    receipt.items["Pizza"].shared_by = [
        ("Alice", None, None),
        ("Bob", None, None),
    ]
    receipt.items["Drinks"].shared_by = [
        ("Alice", None, None)
    ]

    return receipt
