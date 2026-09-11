# Receipt Splitter

A Python CLI app for splitting receipts between people.

## Current Version

**v0.3 — Usable CLI**

## Current Features

- Add multiple people to a receipt
- Add items and their prices
- Confirm and edit people and items
- Assign each item to the people who shared it
- Edit who shared which item
- Split item costs equally between people
- Add a percentage service charge
- Add extra charges, percentage or fixed
- Uses `Decimal` for monetary calculations
- Handles monetary rounding so individual totals match the receipt total
- Comprehensive input validation
- Displays a formatted final receipt with:
  - Item costs
  - Who shared each item
  - Subtotal
  - Service charge
  - Extra charges
  - Receipt total
  - Amount owed by each person
  - Total of amount owed (should match receipt total)

## Example Receipt

After following the prompts, an example ending screen with the full receipt details is shown below:

<table><tr><td>

```text
=============================================
                   RECEIPT
=============================================

PEOPLE: Alice, Bob

ITEMS
---------------------------------------------
Pizza                                £ 9.99
  Shared by: Alice, Bob
Chips                                £ 3.99
  Shared by: Alice
---------------------------------------------
Subtotal                            £ 13.98
Service charge (10%)                 £ 1.40
Extra charge (fixed)                 £ 1.99

---------------------------------------------
Total                               £ 17.37


AMOUNT OWED
---------------------------------------------
Alice                               £ 10.88
Bob                                  £ 6.49
---------------------------------------------
Total                               £ 17.37
---------------------------------------------
```
</td></tr></table>

## Roadmap

### v0.1 — Initial Prototype
- ✓ Basic receipt splitting
- ✓ Multiple people and items
- ✓ Equal item splitting
- ✓ Service charge calculation
- ✓ Basic receipt output

### v0.2 — Clean Prototype
- ✓ Proper program structure
- ✓ Basic input validation
- ✓ Robust monetary rounding
- ✓ Improved receipt formatting

### v0.3 — Usable CLI (current)
- ✓ Comprehensive input validation
- ✓ Confirm and edit people and items
- ✓ More flexible extra charges
- ✓ Clean receipt formatting

### v0.4 — More Powerful Splitting
- Unequal splitting
- Save and load receipts

### v0.5 — Finished CLI
- Finalise CLI functionality
- Package as a standalone executable


### Future
- Web application
- Receipt image scanning / OCR
- Automatic item and price extraction
- User confirmation and correction of scanned receipts
