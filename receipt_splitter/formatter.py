"""Receipt formatter for the receipt splitter."""

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP

from .models import Receipt, ChargeType
from .calculator import calculate_subtotal, calculate_receipt_total, calculate_people_total


@dataclass
class ReceiptFormat:
    line_width: int = 45
    amount_width: int = 7
    label_width: int = line_width - amount_width - 3
    currency: str = "£"


def _divider(format: ReceiptFormat, char: str = "-") -> str:
    return char * format.line_width


def _money_row(
    format: ReceiptFormat,
    label: str,
    amount: Decimal,
) -> str:
    amount = amount.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    money = f"{format.currency} {amount:.2f}"

    return (
        f"{label:<{format.label_width}} {money:>{format.amount_width}}"
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

    lines.append("\nPEOPLE: " + ", ".join(receipt.people))

    lines.append("\nITEMS")
    lines.append(_divider(format))

    for item in receipt.items.values():
        lines.append(_money_row(format, item.name, item.price))
        if item.shared_by:
            names = ", ".join(item.shared_by)
            lines.append(f"  Shared by: {names}")


    subtotal = calculate_subtotal(receipt)

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

    for charge in receipt.extra_charges:
        if charge.type == ChargeType.PERCENTAGE:
            charge_amount = subtotal * charge.value
            percentage = f"{charge.value * 100:.2f}".rstrip("0").rstrip(".")

            lines.append(
                _money_row(
                    format,
                    f"Extra charge ({percentage}%)",
                    charge_amount,
                )
            )

        elif charge.type == ChargeType.FIXED:
            lines.append(
                _money_row(
                    format,
                    "Extra charge (fixed)",
                    charge.value,
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
