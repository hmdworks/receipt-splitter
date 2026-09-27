from decimal import Decimal

from receipt_splitter.models import Receipt, find_key_ci


def test_add_person():
    receipt = Receipt()
    receipt.add_person("Alice")

    assert "Alice" in receipt.people
    assert receipt.people["Alice"].name == "Alice"
    assert receipt.people["Alice"].total == Decimal(0)


def test_add_item():
    receipt = Receipt()
    receipt.add_item("Pizza", Decimal("10.00"))

    assert receipt.items["Pizza"].price == Decimal("10.00")
    assert receipt.items["Pizza"].shared_by == []


def test_rename_person():
    receipt = Receipt()
    receipt.add_person("Alice")
    receipt.rename_person("Alice", "Alicia")

    assert "Alice" not in receipt.people
    assert receipt.people["Alicia"].name == "Alicia"


def test_rename_person_preserves_total():
    receipt = Receipt()
    receipt.add_person("Alice")
    receipt.people["Alice"].total = Decimal("5.00")
    receipt.rename_person("Alice", "Alicia")

    assert receipt.people["Alicia"].total == Decimal("5.00")


def test_remove_person():
    receipt = Receipt()
    receipt.add_person("Alice")
    receipt.add_person("Bob")
    receipt.remove_person("Alice")

    assert "Alice" not in receipt.people
    assert "Bob" in receipt.people


def test_edit_item():
    receipt = Receipt()
    receipt.add_item("Pizza", Decimal("10.00"))
    receipt.edit_item("Pizza", "Pizza Large", Decimal("15.00"))

    assert "Pizza" not in receipt.items
    assert receipt.items["Pizza Large"].price == Decimal("15.00")


def test_edit_item_preserves_shared_by():
    receipt = Receipt()
    receipt.add_item("Pizza", Decimal("10.00"))
    receipt.items["Pizza"].shared_by = ["placeholder"]
    receipt.edit_item("Pizza", "Pizza Large", Decimal("15.00"))

    assert receipt.items["Pizza Large"].shared_by == ["placeholder"]


def test_remove_item():
    receipt = Receipt()
    receipt.add_item("Pizza", Decimal("10.00"))
    receipt.add_item("Drinks", Decimal("5.00"))
    receipt.remove_item("Pizza")

    assert "Pizza" not in receipt.items
    assert "Drinks" in receipt.items


def test_find_key_ci_match():
    assert find_key_ci({"Alice": 1, "Bob": 2}, "alice") == "Alice"


def test_find_key_ci_exact_case():
    assert find_key_ci({"Alice": 1}, "Alice") == "Alice"


def test_find_key_ci_no_match():
    assert find_key_ci({"Alice": 1}, "Charlie") is None
