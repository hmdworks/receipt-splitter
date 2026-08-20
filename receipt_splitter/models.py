"""Data structures for the receipt splitter."""

from dataclasses import dataclass, field
from decimal import Decimal


@dataclass
class Person:
    name: str
    total: Decimal = Decimal("0")


@dataclass
class ReceiptItem:
    name: str
    price: Decimal
    shared_by: list[str] = field(default_factory=list)


@dataclass
class Receipt:
    people: dict[str, Person] = field(default_factory=dict)
    items: dict[str, ReceiptItem] = field(default_factory=dict)
    service_rate: Decimal = Decimal("0")
 
    def add_person(self, name: str) -> None:
        self.people[name] = Person(name)
 
    def add_item(self, name: str, price: Decimal) -> None:
        self.items[name] = ReceiptItem(name, price)