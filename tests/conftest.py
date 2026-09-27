from decimal import Decimal

import pytest

from receipt_splitter.models import Charge, ChargeType, Person, Receipt, ReceiptItem, Share


@pytest.fixture
def sample_receipt():
    receipt = Receipt(
        service_rate=Decimal("0.10"),
        extra_charges=[
            Charge(ChargeType.PERCENTAGE, Decimal("0.05"), None),
            Charge(ChargeType.FIXED, Decimal("2.00"), None),
        ],
    )

    receipt.people = {
        "Alice": Person("Alice"),
        "Bob": Person("Bob"),
    }

    receipt.items = {
        "Pizza": ReceiptItem("Pizza", Decimal("20.00")),
        "Drinks": ReceiptItem("Drinks", Decimal("10.00"))
    }

    receipt.items["Pizza"].shared_by = [
        Share("Alice", None),
        Share("Bob", None),
    ]
    receipt.items["Drinks"].shared_by = [
        Share("Alice", None)
    ]

    return receipt
