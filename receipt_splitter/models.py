"""Data structures for the receipt splitter."""

from dataclasses import dataclass
from decimal import Decimal


@dataclass
class ReceiptItem:
    name: str
    price: Decimal
    shared_by: list[str]


@dataclass
class Receipt:
    people: list[str]
    items: list[ReceiptItem]
    service_rate: Decimal = Decimal("0")