"""Data structures for the receipt splitter."""

from dataclasses import dataclass, field
from decimal import Decimal
from enum import Enum


class ChargeType(Enum):
    PERCENTAGE = "percentage"
    FIXED = "fixed"


@dataclass
class Person:
    name: str
    total: Decimal = Decimal(0)


@dataclass
class ReceiptItem:
    name: str
    price: Decimal
    shared_by: list[tuple[str, Decimal | None]] = field(default_factory=list)


@dataclass
class Charge:
    type: ChargeType
    value: Decimal


def find_key_ci(d: dict[str, object], name: str) -> str | None:
    """Return the actual dict key matching 'name' (case-insensitive), or None."""
    for key in d:
        if key.lower() == name.lower():
            return key
    return None


@dataclass
class Receipt:
    people: dict[str, Person] = field(default_factory=dict)
    items: dict[str, ReceiptItem] = field(default_factory=dict)
    service_rate: Decimal = Decimal(0)
    extra_charges: list[Charge] = field(default_factory=list)

    def add_person(self, name: str) -> None:
        self.people[name] = Person(name)

    def add_item(self, name: str, price: Decimal) -> None:
        self.items[name] = ReceiptItem(name, price)

    def rename_person(self, old_name: str, new_name: str) -> None:
        self.people[old_name].name = new_name
        self.people = {
            new_name if k == old_name else k: v for k, v in self.people.items()
        }

    def remove_person(self, name: str) -> None:
        del self.people[name]

    def edit_item(self, old_name: str, new_name: str, price: Decimal) -> None:
        item = self.items[old_name]
        item.name, item.price = new_name, price
        self.items = {
            new_name if k == old_name else k: v for k, v in self.items.items()
        }

    def remove_item(self, name: str) -> None:
        del self.items[name]
