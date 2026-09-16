"""Receipt formatter for the receipt splitter."""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from .calculator import (
    calculate_people_total,
    calculate_receipt_total,
    calculate_subtotal,
)
from .models import ChargeType, Receipt, WeightType


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

    return f"{label:<{format.label_width}} {money:>{format.amount_width}}"


def format_receipt(
    receipt: Receipt,
    format: ReceiptFormat | None = None,
) -> str:
    """Formats the receipt details into a single string and returns it."""
    if format is None:
        format = ReceiptFormat()

    lines = []

    lines.append(_divider(format, "="))
    lines.append("RECEIPT".center(format.line_width))
    lines.append(_divider(format, "="))

    if receipt.people:
        lines.append("\nPEOPLE: " + ", ".join(receipt.people))

    if receipt.items:
        lines.append("\nITEMS")
        lines.append(_divider(format))

        for item in receipt.items.values():
            lines.append(_money_row(format, item.name, item.price))
            if item.shared_by and len(receipt.people) > 1:
                shared_names = []
                for entry in item.shared_by:
                    person_name = entry[0]
                    person_weight = entry[1]
                    share_type = entry[2]

                    if share_type == WeightType.PERCENTAGE:
                        percentage = person_weight * 100
                        shared_names.append(f"{person_name} ({percentage.normalize():f}%)")
                    elif share_type == WeightType.SHARES:
                        shared_names.append(f"{person_name} ({person_weight})")
                    else:
                        shared_names.append(person_name)

                lines.append(f"  Shared by: {', '.join(shared_names)}")

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
    format: ReceiptFormat | None = None,
) -> str:
    """Formats amount owed by every person and people total into a single string and returns it."""
    if format is None:
        format = ReceiptFormat()

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
