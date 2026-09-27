from decimal import Decimal

import pytest

from receipt_splitter.models import Charge, ChargeType, Receipt, Share


@pytest.fixture
def sample_receipt():
    receipt = Receipt(
        service_rate=Decimal("0.10"),
        extra_charges=[
            Charge(ChargeType.PERCENTAGE, Decimal("0.05"), None),
            Charge(ChargeType.FIXED, Decimal("2.00"), None),
        ],
    )

    receipt.add_person("Alice")
    receipt.add_person("Bob")

    receipt.add_item("Pizza", Decimal("20.00"))
    receipt.add_item("Drinks", Decimal("10.00"))

    receipt.items["Pizza"].shared_by = [
        Share("Alice", None),
        Share("Bob", None),
    ]
    receipt.items["Drinks"].shared_by = [
        Share("Alice", None)
    ]

    return receipt
