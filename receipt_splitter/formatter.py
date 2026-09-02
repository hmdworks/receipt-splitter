"""Receipt formatter for the receipt splitter."""

from dataclasses import dataclass
from decimal import Decimal

from .models import Receipt
from .calculator import calculate_subtotal, calculate_receipt_total, calculate_people_total


@dataclass
class ReceiptFormat:
    line_width: int = 40
    label_width: int = 25
    amount_width: int = 8
    currency: str = "£"


def _divider(format: ReceiptFormat, char: str = "-") -> str:
    return char * format.line_width


def _money_row(
    format: ReceiptFormat,
    label: str,
    amount: Decimal,
) -> str:
    return (
        f"{label:<{format.label_width}} "
        f"{format.currency}{amount:>{format.amount_width}.2f}"
    )


def format_receipt(
    receipt: Receipt,
    format: ReceiptFormat = ReceiptFormat(),
) -> str:
    """Build the receipt as a single string and returns it. No printing..."""
    lines = []

    lines.append(_divider(format, "="))
    lines.append("RECEIPT".center(format.line_width))
    lines.append(_divider(format, "="))
 
    lines.append("\nITEMS")
    lines.append(_divider(format))


    subtotal = calculate_subtotal(receipt)

    for item in receipt.items.values():
        names = ", ".join(item.shared_by)
        lines.append(_money_row(format, item.name, item.price))
        lines.append(f"  Shared by: {names}")

    lines.append(_divider(format))
    lines.append(_money_row(format, "Subtotal", subtotal))

    if receipt.service_rate > 0:
        service_charge = subtotal * receipt.service_rate
        percentage = f"{receipt.service_rate * 100:.2f}".rstrip("0").rstrip(".")

        lines.append(
            _money_row(
                format,
                f"Service charge ({percentage}%)",
                service_charge,
            )
        )

    return "\n".join(lines)


def format_amount_owed(
    receipt: Receipt,
    format: ReceiptFormat = ReceiptFormat(),
) -> str:
    
    lines = []
    total = calculate_receipt_total(receipt)

    lines.append(_divider(format))
    lines.append(_money_row(format, "Total", total))

    lines.append("\n\nAMOUNT OWED")
    lines.append(_divider(format))

    for person in receipt.people.values():
        lines.append(_money_row(format, person.name, person.total))

    lines.append(_divider(format))
    lines.append(
        _money_row(
            format,
            "Total",
            calculate_people_total(receipt),
        )
    )
    lines.append(_divider(format))

    return "\n".join(lines)


def show_receipt(receipt: Receipt) -> None:
    print("\n" + format_receipt(receipt))


def show_amount_owed(receipt: Receipt) -> None:
    print("\n" + format_amount_owed(receipt))
