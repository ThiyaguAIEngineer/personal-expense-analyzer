# Personal Expense Analyzer

A Week 1 vibe-coding project that turns transaction CSV files into an interactive personal-spending dashboard. The application uses pandas to validate and prepare uploaded data, then presents spending KPIs, filters, charts, and searchable transactions in Streamlit.

## Problem Statement

Transaction exports can be difficult to review in raw CSV form. This project provides a simple way to upload a transaction file, clean inconsistent values, and explore spending patterns without changing the source data.

## Key Features

- Uploads transaction CSV files directly in the dashboard.
- Validates the expected schema and cleans data with pandas.
- Supports date, category, merchant, and payment-method filters.
- Calculates total spending, unique transactions, average transaction value, top spending category, and highest single transaction.
- Displays interactive Plotly charts for category, date, day type, weekly, merchant, and item spending.
- Includes a transaction search across merchant, item, category, and transaction ID.
- Handles unreadable files, missing required columns, invalid rows, files with no usable transactions, and empty filter or search results gracefully.

## Tech Stack

- Python 3.13+
- Streamlit
- pandas
- Plotly
- uv for dependency and environment management

## Architecture and Data Flow

```text
CSV Upload
    ↓
Schema Validation
    ↓
Pandas Cleaning
    ↓
Derived Fields
    ↓
Global Filters
    ↓
Metrics + Aggregations
    ↓
Streamlit + Plotly Dashboard
```

## Expected CSV Schema

The CSV must include these columns:

| Column | Description |
| --- | --- |
| `Transaction_ID` | Identifier for a transaction; multiple rows may share one ID. |
| `Date` | Transaction date in a pandas-recognized date format. |
| `Merchant` | Merchant name. |
| `Item` | Purchased item or description. |
| `Category` | Spending category. |
| `Amount` | Transaction amount; US-style currency and parenthesized negative values are supported. |
| `Payment_Method` | Payment method used. |

These columns are optional: `Time`, `Quantity`, and `Unit`.

## Data Cleaning Behavior

- Rejects uploads that are missing required columns.
- Removes exact duplicate input rows.
- Trims text values, collapses repeated whitespace, and replaces empty merchant, item, category, and payment-method values with `Unknown`.
- Parses dates and amounts; rows with an unusable transaction ID, date, or amount are removed and reported.
- Normalizes merchant capitalization, selected category aliases (for example, food to Dining), and common payment-method aliases (such as CC to Credit Card).
- Normalizes supplied times when possible and adds derived year, month, ISO week, day-of-week, and weekday/weekend fields.

## Dashboard Capabilities

The dashboard provides three tabs:

- **Overview:** Spending by category, spending over time, and weekday versus weekend spending.
- **Spending Analysis:** Weekly spending plus the top 10 merchants and items by spending.
- **Transactions:** A filtered transaction table with case-insensitive text search.

All charts and KPIs respect the active sidebar filters. Refunds and other negative amounts remain included in spending calculations.

## Installation

Install dependencies and create the local environment with uv:

```powershell
uv sync
```

## Run Locally

Start the Streamlit application from the project root:

```powershell
uv run streamlit run src/vibe_coding_basics/app.py
```

Then open the local URL shown by Streamlit, typically `http://localhost:8501`.

## Project Structure

```text
.
|-- .streamlit/
|   `-- config.toml                 # Streamlit theme configuration
|-- src/
|   `-- vibe_coding_basics/
|       |-- app.py                  # Streamlit dashboard and visualizations
|       |-- data_cleaning.py        # CSV validation and cleaning helpers
|       |-- metrics.py              # KPI and grouped spending calculations
|       `-- __init__.py
|-- pyproject.toml                  # Project metadata and dependencies
|-- uv.lock                         # Locked dependency versions
`-- README.md
```

## AI-Assisted Vibe Coding Workflow

The project began by defining the problem statement, CSV schema, dashboard requirements, and a focused MVP scope. Codex was then asked to inspect the existing project and propose a plan before code was written.

Key implementation decisions were reviewed before and during development, including transaction grouping, duplicate handling, date formats, and the required CSV fields. The app was built incrementally in these phases:

1. Data validation and cleaning
2. Spending metrics
3. Streamlit upload flow and filters
4. KPI cards
5. Plotly charts and transaction search
6. UI refinement

Each phase was tested before moving forward, and generated code was reviewed with edge cases investigated rather than accepted blindly. During testing, the ambiguous non-US amount format `2,50` was identified; the amount-cleaning rule was updated to reject invalid comma groupings instead of interpreting that value as a US-style amount.

AI accelerated implementation and iteration, while human review, testing, and product decisions remained part of the workflow.

## Key Learnings

- A small Streamlit application can provide useful analysis with a focused data-cleaning layer and a few clear visualizations.
- Validating uploaded data before calculating metrics makes dashboard behavior more reliable.
- Separating cleaning, metric calculations, and UI code keeps the project easier to extend and maintain.
- Thoughtful filters, feedback states, and readable charts improve the usability of a data dashboard.

## Future Enhancements

- Add recurring-transaction detection; this is not currently implemented.
- Add downloadable filtered-data exports.
- Add additional time-based views, such as monthly spending trends.
