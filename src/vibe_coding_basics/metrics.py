"""Spending metrics and grouped summaries for cleaned expense data."""

from typing import Optional

import pandas as pd


def total_spending(data: pd.DataFrame) -> float:
    """Return the sum of all row amounts, including refunds."""
    if data.empty:
        return 0.0
    return float(data["Amount"].sum())


def transaction_totals(data: pd.DataFrame) -> pd.Series:
    """Return one summed amount for each transaction ID."""
    if data.empty:
        return pd.Series(dtype="float64", name="Amount")
    return data.groupby("Transaction_ID")["Amount"].sum()


def unique_transactions(data: pd.DataFrame) -> int:
    """Count distinct transaction IDs."""
    if data.empty:
        return 0
    return int(data["Transaction_ID"].nunique())


def average_transaction_value(data: pd.DataFrame) -> float:
    """Average transaction totals, after adding together each transaction's rows."""
    totals = transaction_totals(data)
    if totals.empty:
        return 0.0
    return float(totals.mean())


def highest_single_transaction(data: pd.DataFrame) -> float:
    """Return the largest summed transaction total, including negative totals."""
    totals = transaction_totals(data)
    if totals.empty:
        return 0.0
    return float(totals.max())


def spending_by_category(data: pd.DataFrame) -> pd.Series:
    """Return total spending per category, sorted from highest to lowest."""
    if data.empty:
        return pd.Series(dtype="float64", name="Amount")
    return data.groupby("Category")["Amount"].sum().sort_values(ascending=False)


def top_spending_category(data: pd.DataFrame) -> Optional[str]:
    """Return the category with the highest summed amount, or None if empty."""
    totals = spending_by_category(data)
    if totals.empty:
        return None
    return str(totals.index[0])


def spending_by_date(data: pd.DataFrame) -> pd.Series:
    """Return total spending per date, sorted chronologically."""
    if data.empty:
        return pd.Series(dtype="float64", name="Amount")
    return data.groupby("Date")["Amount"].sum().sort_index()


def spending_by_year_week(data: pd.DataFrame) -> pd.Series:
    """Return total spending per ISO year-week, sorted by year-week label."""
    if data.empty:
        return pd.Series(dtype="float64", name="Amount")
    return data.groupby("Year_Week")["Amount"].sum().sort_index()


def spending_by_day_type(data: pd.DataFrame) -> pd.Series:
    """Return total spending for each day type, sorted by spending amount."""
    if data.empty:
        return pd.Series(dtype="float64", name="Amount")
    return data.groupby("Day_Type")["Amount"].sum().sort_values(ascending=False)


def spending_by_merchant(data: pd.DataFrame) -> pd.Series:
    """Return total spending per merchant, sorted from highest to lowest."""
    if data.empty:
        return pd.Series(dtype="float64", name="Amount")
    return data.groupby("Merchant")["Amount"].sum().sort_values(ascending=False)


def spending_by_item(data: pd.DataFrame) -> pd.Series:
    """Return total spending per item, sorted from highest to lowest."""
    if data.empty:
        return pd.Series(dtype="float64", name="Amount")
    return data.groupby("Item")["Amount"].sum().sort_values(ascending=False)
