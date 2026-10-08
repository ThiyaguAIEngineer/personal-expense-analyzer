"""Validation and cleaning helpers for uploaded expense CSV data."""

from datetime import datetime
from typing import Any

import pandas as pd


REQUIRED_COLUMNS = [
    "Transaction_ID",
    "Date",
    "Merchant",
    "Item",
    "Category",
    "Amount",
    "Payment_Method",
]

OPTIONAL_COLUMNS = ["Time", "Quantity", "Unit"]


def validate_csv_schema(data: pd.DataFrame) -> list[str]:
    """Return required column names that are missing from the input."""
    return [column for column in REQUIRED_COLUMNS if column not in data.columns]


def _clean_text_column(series: pd.Series) -> pd.Series:
    """Trim whitespace and collapse repeated spaces in text values."""
    text = series.astype("string").str.strip().str.replace(r"\s+", " ", regex=True)
    return text.mask(text.eq(""), pd.NA)


def _normalize_category(value: Any) -> Any:
    if pd.isna(value):
        return "Unknown"

    cleaned = str(value).strip()
    aliases = {"dining": "Dining", "food": "Dining", "groceries": "Groceries"}
    return aliases.get(cleaned.casefold(), cleaned.title())


def _normalize_payment_method(value: Any) -> Any:
    if pd.isna(value):
        return "Unknown"

    cleaned = str(value).strip()
    aliases = {
        "cc": "Credit Card",
        "credit card": "Credit Card",
        "debit card": "Debit Card",
    }
    return aliases.get(cleaned.casefold(), cleaned.title())


def _parse_time(value: Any) -> str:
    """Parse common 12-hour and 24-hour time strings into HH:MM:SS."""
    if pd.isna(value) or not str(value).strip():
        return "Unknown"

    cleaned = str(value).strip().upper()
    formats = ["%I:%M %p", "%I:%M%p", "%I %p", "%I%p", "%H:%M:%S", "%H:%M"]
    for time_format in formats:
        try:
            return datetime.strptime(cleaned, time_format).strftime("%H:%M:%S")
        except ValueError:
            continue
    return "Unknown"


def _parse_amount(series: pd.Series) -> pd.Series:
    """Parse US-style amounts and reject malformed comma groupings."""
    text = series.astype("string").str.strip()

    # Parentheses are a common way to show a negative financial amount.
    parenthesized = text.str.fullmatch(r"\(\s*\$?\s*[^()]+\s*\)", na=False)
    text = text.str.replace(r"^\(\s*\$?\s*([^()]+)\s*\)$", r"-\1", regex=True)
    text = text.str.replace("$", "", regex=False).str.strip()

    # Commas must separate groups of three digits, as in 1,234 or 12,345.67.
    valid_format = text.str.fullmatch(
        r"-?(?:\d+|\d{1,3}(?:,\d{3})+)(?:\.\d+)?", na=False
    )
    text = text.where(valid_format).str.replace(",", "", regex=False)
    amounts = pd.to_numeric(text, errors="coerce")

    # A parenthesized amount must contain a valid positive amount before negation.
    return amounts.where(~parenthesized | amounts.lt(0))


def clean_expense_data(data: pd.DataFrame) -> tuple[pd.DataFrame, dict[str, Any]]:
    """Validate and clean expense rows, returning clean data and quality counts.

    Rows with unusable transaction IDs, dates, or amounts are removed. Only
    identical input rows are removed as duplicates. The input DataFrame is not
    modified.
    """
    missing_columns = validate_csv_schema(data)
    if missing_columns:
        missing = ", ".join(missing_columns)
        raise ValueError(f"CSV is missing required columns: {missing}")

    quality: dict[str, Any] = {
        "input_rows": len(data),
        "missing_optional_columns": [
            column for column in OPTIONAL_COLUMNS if column not in data.columns
        ],
    }

    # Compare raw rows so cleanup cannot make distinct input rows look like duplicates.
    cleaned = data.drop_duplicates().copy()
    quality["exact_duplicate_rows_removed"] = len(data) - len(cleaned)

    cleaned["Transaction_ID"] = _clean_text_column(cleaned["Transaction_ID"])
    cleaned["Date"] = pd.to_datetime(
        cleaned["Date"], format="mixed", dayfirst=False, errors="coerce"
    ).dt.normalize()
    cleaned["Amount"] = _parse_amount(cleaned["Amount"])

    invalid_id = cleaned["Transaction_ID"].isna()
    invalid_date = cleaned["Date"].isna()
    invalid_amount = cleaned["Amount"].isna()
    unusable = invalid_id | invalid_date | invalid_amount

    quality["unusable_rows_removed"] = int(unusable.sum())
    quality["invalid_transaction_id_rows"] = int(invalid_id.sum())
    quality["invalid_date_rows"] = int(invalid_date.sum())
    quality["invalid_amount_rows"] = int(invalid_amount.sum())

    cleaned = cleaned.loc[~unusable].copy()

    for column in ["Merchant", "Item", "Category", "Payment_Method"]:
        cleaned[column] = _clean_text_column(cleaned[column]).fillna("Unknown")

    cleaned["Merchant"] = cleaned["Merchant"].str.title()
    cleaned["Category"] = cleaned["Category"].map(_normalize_category)
    cleaned["Payment_Method"] = cleaned["Payment_Method"].map(
        _normalize_payment_method
    )

    if "Time" in cleaned.columns:
        cleaned["Time"] = cleaned["Time"].map(_parse_time)
    else:
        cleaned["Time"] = "Unknown"

    if "Quantity" in cleaned.columns:
        cleaned["Quantity"] = pd.to_numeric(cleaned["Quantity"], errors="coerce")
    else:
        cleaned["Quantity"] = pd.NA

    if "Unit" in cleaned.columns:
        cleaned["Unit"] = _clean_text_column(cleaned["Unit"]).fillna("Unknown")
    else:
        cleaned["Unit"] = "Unknown"

    iso_dates = cleaned["Date"].dt.isocalendar()
    cleaned["Year"] = cleaned["Date"].dt.year
    cleaned["Month"] = cleaned["Date"].dt.month
    cleaned["Month_Year"] = cleaned["Date"].dt.strftime("%Y-%m")
    cleaned["Week"] = iso_dates.week.astype(int)
    cleaned["Year_Week"] = (
        iso_dates.year.astype(str) + "-W" + iso_dates.week.astype(str).str.zfill(2)
    )
    cleaned["Day_of_Week"] = cleaned["Date"].dt.day_name()
    cleaned["Day_Type"] = cleaned["Date"].dt.dayofweek.map(
        lambda day: "Weekend" if day >= 5 else "Weekday"
    )

    quality["cleaned_rows"] = len(cleaned)
    quality["total_rows_removed"] = len(data) - len(cleaned)
    return cleaned.reset_index(drop=True), quality
