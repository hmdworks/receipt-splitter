from decimal import Decimal

import pytest

from receipt_splitter import validation


# ------------------------------------------------------------------
# validate_person_names
# ------------------------------------------------------------------

def test_validate_person_names_valid():
    assert validation.validate_person_names("Alice, Bob, Charlie") == [
        "Alice", "Bob", "Charlie"
    ]


def test_validate_person_names_strips_whitespace():
    assert validation.validate_person_names(" Alice ,  Bob ") == ["Alice", "Bob"]


def test_validate_person_names_empty_raises():
    with pytest.raises(ValueError):
        validation.validate_person_names("")


def test_validate_person_names_whitespace_only_raises():
    with pytest.raises(ValueError):
        validation.validate_person_names("   ")


def test_validate_person_names_duplicate_case_insensitive_raises():
    with pytest.raises(ValueError):
        validation.validate_person_names("Alice, alice")


def test_validate_person_names_blank_entry_raises():
    with pytest.raises(ValueError):
        validation.validate_person_names("Alice, , Bob")


def test_validate_person_names_no_letters_raises():
    with pytest.raises(ValueError):
        validation.validate_person_names("123, Bob")


# ------------------------------------------------------------------
# validate_new_person_name
# ------------------------------------------------------------------

def test_validate_new_person_name_valid():
    assert validation.validate_new_person_name("Charlie", ["Alice", "Bob"]) == "Charlie"


def test_validate_new_person_name_empty_raises():
    with pytest.raises(ValueError):
        validation.validate_new_person_name("   ", [])


def test_validate_new_person_name_no_letters_raises():
    with pytest.raises(ValueError):
        validation.validate_new_person_name("123", [])


def test_validate_new_person_name_duplicate_case_insensitive_raises():
    with pytest.raises(ValueError):
        validation.validate_new_person_name("alice", ["Alice"])


# ------------------------------------------------------------------
# validate_item_line
# ------------------------------------------------------------------

def test_validate_item_line_valid():
    assert validation.validate_item_line("Pizza, 12.50") == ("Pizza", "12.50")


def test_validate_item_line_no_comma_raises():
    with pytest.raises(ValueError):
        validation.validate_item_line("Pizza 12.50")


def test_validate_item_line_splits_on_first_comma_only():
    assert validation.validate_item_line("Pizza, 12.50, extra") == (
        "Pizza",
        "12.50, extra",
    )


# ------------------------------------------------------------------
# validate_item_name
# ------------------------------------------------------------------

def test_validate_item_name_new_valid():
    assert validation.validate_item_name("Pizza", ["Drinks"], False) == "Pizza"


def test_validate_item_name_new_duplicate_case_insensitive_raises():
    with pytest.raises(ValueError):
        validation.validate_item_name("pizza", ["Pizza"], False)


def test_validate_item_name_new_empty_raises():
    with pytest.raises(ValueError):
        validation.validate_item_name("  ", [], False)


def test_validate_item_name_existing_valid():
    assert validation.validate_item_name("pizza", ["Pizza"], True) == "pizza"


def test_validate_item_name_existing_not_found_raises():
    with pytest.raises(ValueError):
        validation.validate_item_name("Drinks", ["Pizza"], True)


# ------------------------------------------------------------------
# validate_item
# ------------------------------------------------------------------

def test_validate_item_valid():
    name, price = validation.validate_item("Pizza, 12.50", [])
    assert name == "Pizza"
    assert price == Decimal("12.50")


def test_validate_item_bad_price_raises():
    with pytest.raises(ValueError):
        validation.validate_item("Pizza, free", [])


def test_validate_item_duplicate_name_raises():
    with pytest.raises(ValueError):
        validation.validate_item("Pizza, 12.50", ["Pizza"])


# ------------------------------------------------------------------
# validate_price
# ------------------------------------------------------------------

def test_validate_price_valid():
    assert validation.validate_price("12.50") == Decimal("12.50")


def test_validate_price_integer_ok():
    assert validation.validate_price("12") == Decimal("12")


def test_validate_price_not_a_number_raises():
    with pytest.raises(ValueError):
        validation.validate_price("abc")


def test_validate_price_zero_raises():
    with pytest.raises(ValueError):
        validation.validate_price("0")


def test_validate_price_negative_raises():
    with pytest.raises(ValueError):
        validation.validate_price("-5")


def test_validate_price_too_many_decimals_raises():
    with pytest.raises(ValueError):
        validation.validate_price("12.505")


# ------------------------------------------------------------------
# validate_shared_names
# ------------------------------------------------------------------

@pytest.fixture
def people():
    return {"Alice": object(), "Bob": object()}


def test_validate_shared_names_all(people):
    assert validation.validate_shared_names("all", people) == ["Alice", "Bob"]


def test_validate_shared_names_specific(people):
    assert validation.validate_shared_names("Alice", people) == ["Alice"]


def test_validate_shared_names_case_insensitive_lookup(people):
    assert validation.validate_shared_names("alice, BOB", people) == ["alice", "BOB"]


def test_validate_shared_names_unknown_raises(people):
    with pytest.raises(ValueError):
        validation.validate_shared_names("Charlie", people)


def test_validate_shared_names_blank_entry_raises(people):
    with pytest.raises(ValueError):
        validation.validate_shared_names("Alice, ", people)


def test_validate_shared_names_duplicate_raises(people):
    with pytest.raises(ValueError):
        validation.validate_shared_names("Alice, alice", people)


# ------------------------------------------------------------------
# validate_yes_no
# ------------------------------------------------------------------

def test_validate_yes_no_yes():
    assert validation.validate_yes_no("y") is True


def test_validate_yes_no_no_case_insensitive():
    assert validation.validate_yes_no("N") is False


def test_validate_yes_no_invalid_raises():
    with pytest.raises(ValueError):
        validation.validate_yes_no("maybe")


# ------------------------------------------------------------------
# validate_percentage_charge
# ------------------------------------------------------------------

def test_validate_percentage_charge_no_label():
    value, label = validation.validate_percentage_charge("10")
    assert value == Decimal("0.10")
    assert label is None


def test_validate_percentage_charge_with_label():
    value, label = validation.validate_percentage_charge("10 tax")
    assert value == Decimal("0.10")
    assert label == "tax"


def test_validate_percentage_charge_label_no_letters_raises():
    with pytest.raises(ValueError):
        validation.validate_percentage_charge("10 123")


def test_validate_percentage_charge_not_a_number_raises():
    with pytest.raises(ValueError):
        validation.validate_percentage_charge("abc")


def test_validate_percentage_charge_negative_raises():
    with pytest.raises(ValueError):
        validation.validate_percentage_charge("-5")


def test_validate_percentage_charge_over_100_raises():
    with pytest.raises(ValueError):
        validation.validate_percentage_charge("101")


def test_validate_percentage_charge_exactly_100_ok():
    value, _ = validation.validate_percentage_charge("100")
    assert value == Decimal("1")


# ------------------------------------------------------------------
# validate_fixed_charge
# ------------------------------------------------------------------

def test_validate_fixed_charge_no_label():
    value, label = validation.validate_fixed_charge("5")
    assert value == Decimal("5")
    assert label is None


def test_validate_fixed_charge_with_label():
    value, label = validation.validate_fixed_charge("5 tip")
    assert value == Decimal("5")
    assert label == "tip"


def test_validate_fixed_charge_negative_raises():
    with pytest.raises(ValueError):
        validation.validate_fixed_charge("-5")


def test_validate_fixed_charge_zero_ok():
    value, _ = validation.validate_fixed_charge("0")
    assert value == Decimal("0")


def test_validate_fixed_charge_not_a_number_raises():
    with pytest.raises(ValueError):
        validation.validate_fixed_charge("abc")


def test_validate_fixed_charge_label_no_letters_raises():
    with pytest.raises(ValueError):
        validation.validate_fixed_charge("5 123")


# ------------------------------------------------------------------
# validate_num_option
# ------------------------------------------------------------------

def test_validate_num_option_valid():
    assert validation.validate_num_option("3", 5) == 3


def test_validate_num_option_out_of_range_raises():
    with pytest.raises(ValueError):
        validation.validate_num_option("6", 5)


def test_validate_num_option_zero_raises():
    with pytest.raises(ValueError):
        validation.validate_num_option("0", 5)


def test_validate_num_option_not_a_number_raises():
    with pytest.raises(ValueError):
        validation.validate_num_option("abc", 5)


# ------------------------------------------------------------------
# validate_shares_input
# ------------------------------------------------------------------

def test_validate_shares_input_valid():
    assert validation.validate_shares_input("3") == Decimal("3")


def test_validate_shares_input_zero_raises():
    with pytest.raises(ValueError):
        validation.validate_shares_input("0")


def test_validate_shares_input_negative_raises():
    with pytest.raises(ValueError):
        validation.validate_shares_input("-1")


def test_validate_shares_input_not_an_integer_raises():
    with pytest.raises(ValueError):
        validation.validate_shares_input("1.5")


def test_validate_shares_input_not_a_number_raises():
    with pytest.raises(ValueError):
        validation.validate_shares_input("abc")


# ------------------------------------------------------------------
# validate_fast_split_line
# ------------------------------------------------------------------

def test_validate_fast_split_line_valid():
    result = validation.validate_fast_split_line("Pizza, 10, Alice, Bob", {})
    assert result[0] == "Pizza"
    assert result[1] == Decimal("10")
    assert result[2:] == ["Alice", "Bob"]


def test_validate_fast_split_line_empty_with_no_items_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("", {})


def test_validate_fast_split_line_empty_with_items_returns_empty_list():
    assert validation.validate_fast_split_line("", {"Pizza": object()}) == []


def test_validate_fast_split_line_too_few_details_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("Pizza, 10", {})


def test_validate_fast_split_line_blank_detail_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("Pizza, 10, ", {})


def test_validate_fast_split_line_duplicate_item_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("Pizza, 10, Alice", {"Pizza": object()})


def test_validate_fast_split_line_no_letters_in_item_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("123, 10, Alice", {})


def test_validate_fast_split_line_no_letters_in_person_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("Pizza, 10, 123", {})


def test_validate_fast_split_line_duplicate_names_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("Pizza, 10, Alice, alice", {})


def test_validate_fast_split_line_bad_price_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_line("Pizza, free, Alice", {})


# ------------------------------------------------------------------
# validate_fast_split_extra_charges
# ------------------------------------------------------------------

def test_validate_fast_split_extra_charges_empty():
    assert validation.validate_fast_split_extra_charges("") == []


def test_validate_fast_split_extra_charges_valid_mixed():
    result = validation.validate_fast_split_extra_charges("2, 10% tax, 5")
    assert result == [("2", None), ("10%", "tax"), ("5", None)]


def test_validate_fast_split_extra_charges_blank_token_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_extra_charges("2, , 5")


def test_validate_fast_split_extra_charges_label_no_letters_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_extra_charges("2 123")


def test_validate_fast_split_extra_charges_bad_percent_format_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_extra_charges("10%%")


def test_validate_fast_split_extra_charges_not_a_number_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_extra_charges("abc")


def test_validate_fast_split_extra_charges_zero_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_extra_charges("0")


def test_validate_fast_split_extra_charges_too_many_decimals_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_extra_charges("1.005")


def test_validate_fast_split_extra_charges_percent_over_100_raises():
    with pytest.raises(ValueError):
        validation.validate_fast_split_extra_charges("101%")
