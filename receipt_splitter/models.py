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
    total: Decimal = Decimal("0")


@dataclass
class ReceiptItem:
    name: str
    price: Decimal
    shared_by: list[str] = field(default_factory=list)


@dataclass
class Charge:
    type: ChargeType
    value: Decimal


@dataclass
class Receipt:
    people: dict[str, Person] = field(default_factory=dict)
    items: dict[str, ReceiptItem] = field(default_factory=dict)
    service_rate: Decimal = Decimal("0")
    extra_charges: list[Charge] = field(default_factory=list)
 
    def add_person(self, name: str) -> None:
        self.people[name] = Person(name)
 
    def add_item(self, name: str, price: Decimal) -> None:
        self.items[name] = ReceiptItem(name, price)

    def rename_person(self, old_name: str, new_name: str) -> None:
        person = self.people.pop(old_name)
        person.name = new_name
        self.people[new_name] = person

        # reference with shared_by and update
        for item in self.items.values():
            item.shared_by = [
                new_name if name == old_name else name
                for name in item.shared_by
            ]

    def remove_person(self, name: str) -> None:
        del self.people[name]

        # remove the person from any shared items
        for item in self.items.values():
            item.shared_by = [
                person for person in item.shared_by
                if person != name
            ]

    def edit_item(self,
        old_name: str,
        new_name: str,
        price: Decimal,
    ) -> None:
        item = self.items.pop(old_name)
        item.name = new_name
        item.price = price
        self.items[new_name] = item

    def remove_item(self, name: str) -> None:
        del self.items[name]