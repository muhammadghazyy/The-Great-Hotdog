# The Great Hotdog

A small, command-line point-of-sale (POS) prototype for a fictional hotdog stand. This project is being built as a practical way to learn ERP concepts, transaction workflows, and eventually Kubernetes.

## Current Status

**Prototype / learning project - usable locally, not production-ready.**

The current application can:

- Display a menu with hotdogs and drinks.
- Build an order from repeated item selections.
- Check ingredient availability from each product's recipe.
- Calculate a 12% VAT and service-charge amount.
- Accept cash payments and calculate change.
- Generate a dynamic QRIS payment code and attempt payment verification through a webcam and OCR.
- Print a text receipt with a transaction ID.
- Save completed transactions to JSON.
- Deduct used ingredients from inventory.

The current catalog contains Original Hotdog, Cheese Hotdog, and Coke. Store location and timezone are configured in `pos.py`.

## Tech Stack

- **Python 3.14+** - application language and CLI flow
- **JSON** - product, inventory, and transaction persistence
- **PostgreSQL (planned)** - transactional ERP database to replace the JSON datastore
- **Tkinter** - QRIS payment window
- **OpenCV** - webcam capture and image processing
- **EasyOCR** - payment-screen text recognition in English and Indonesian
- **Pillow** - image conversion for the Tkinter UI
- **qrcode** - QR code generation
- **pytz** - timezone-aware transaction IDs and timestamps

There is currently no dependency lockfile or `requirements.txt`; install the Python packages listed above before running the application. Tkinter may also need to be installed separately by the operating system. QRIS mode additionally requires a working camera and the dependencies needed by EasyOCR/OpenCV.

## Getting Started

From the repository root:

```bash
python -m pip install pytz qrcode pillow opencv-python easyocr
python pos.py
```

Use the numbered prompts to add products to the cart, press `n` to finish the cart, and then choose cash or QRIS. Run the command from the repository root because the application loads files using paths under `data/`.

For a syntax-only check:

```bash
python -m py_compile pos.py modules/*.py
```

## Project Structure

```text
.
├── pos.py                 # CLI entry point and order workflow
├── modules/
│   ├── inventory.py       # Recipe-based inventory checks and deductions
│   ├── payment.py         # Cash payment, IDs, and transaction persistence
│   ├── qris.py            # Dynamic QRIS and webcam/OCR verification
│   └── receipt.py         # Menu, cart, and total formatting
├── data/
│   ├── products.json      # Menu, prices, categories, and recipes
│   ├── inventory.json     # Ingredient quantities
│   └── transactions.json  # Historical transaction records
└── assets/
	└── qris.png           # QRIS-related image asset
```

The JSON files are the application's local datastore. Running the POS changes `data/inventory.json` and appends completed orders to `data/transactions.json`. Back up those files before testing with real data.

## Disclaimer

This is an educational prototype, not a production ERP, accounting system, inventory system, or payment gateway. PostgreSQL and the broader ERP modules described below are planned and are not implemented yet. The current application has no authentication, authorization, database transactions, audit log, backup strategy, input hardening, automated test suite, or deployment configuration.

QRIS verification is experimental: it relies on OCR text detected from a camera view and should not be treated as authoritative proof of payment. Do not use this project to process real payments or store sensitive customer or business data. Replace the sample QRIS configuration and review the payment design before any real-world use.

## Future Goals

- Add automated unit and integration tests for pricing, inventory, payment, and QRIS parsing.
- Move persistence from JSON files to PostgreSQL with a schema, migrations, transactional updates, indexes, and backups.
- Add product, ingredient, recipe, and inventory management instead of editing JSON manually.
- Add purchasing and supplier management for purchase orders, receiving, and vendor records.
- Add sales and customer management for order history, customer profiles, refunds, and sales channels.
- Add finance and accounting components for a chart of accounts, tax records, expenses, payments, and reconciliation.
- Add reporting and dashboards for sales, profit, inventory levels, purchasing, and daily summaries.
- Add workforce and operations components for users, roles, permissions, shifts, branches, and point-of-sale terminals.
- Improve validation, error handling, idempotency, and transaction recovery.
- Separate business logic from the CLI and QRIS desktop UI behind clearer application interfaces.
- Add configuration through environment variables or a settings file.
- Containerize the application and explore Kubernetes deployment as the ERP learning phase progresses.
