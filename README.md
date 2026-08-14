# Receipt Splitter

A Python CLI app for splitting receipts between people.

## Current Version

**V0.2 — Clean Prototype**

## Current Features

- Add multiple people to a receipt
- Add items and their prices
- Assign each item to the people who shared it
- Split item costs equally between people
- Add a percentage service charge
- Use `Decimal` for monetary calculations
- Handle monetary rounding so individual totals match the receipt total
- Basic input validation
- Display a final receipt with:
  - Item costs
  - Who shared each item
  - Subtotal
  - Service charge
  - Total
  - Amount owed by each person

## Roadmap

### V0.1 — Initial Prototype
✓ Basic receipt splitting
✓ Multiple people and items
✓ Equal item splitting
✓ Service charge calculation
✓ Basic receipt output

### V0.2 — Clean Prototype (Current)
✓ Proper program structure
✓ Basic input validation
✓ Robust monetary rounding
✓ Improved receipt formatting

### V0.3 — Usable CLI
- Comprehensive input validation
- Confirm and edit people and items
- More flexible extra charges
- Option to split or settle up

### V0.4 — More Powerful Splitting
- Unequal splitting
- Save and load receipts

### V0.5 — Finished CLI
- Finalise CLI functionality
- Package as a standalone executable


### Future
- Web application
- Receipt image scanning / OCR
- Automatic item and price extraction
- User confirmation and correction of scanned receipts
