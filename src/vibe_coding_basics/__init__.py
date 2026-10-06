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
