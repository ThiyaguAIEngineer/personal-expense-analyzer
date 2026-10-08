import pandas as pd


def main() -> None:
    expenses = {
        "Category": ["Food", "Fuel", "Shopping", "Food"],
        "Amount": [120, 50, 200, 80],
    }

    df = pd.DataFrame(expenses)

    print("Expense data:")
    print(df)

    total_expense = df["Amount"].sum()

    print()
    print("Total expense:", total_expense)

    category_totals = df.groupby("Category")["Amount"].sum()

    print()
    print("Expense totals by category:")
    for category, amount in category_totals.items():
        print(f"{category} = {amount}")
