"""Streamlit dashboard for exploring personal expense transactions."""

import pandas as pd
import plotly.express as px
import streamlit as st

from vibe_coding_basics.data_cleaning import clean_expense_data
from vibe_coding_basics.metrics import (
    average_transaction_value,
    highest_single_transaction,
    spending_by_category,
    spending_by_date,
    spending_by_day_type,
    spending_by_item,
    spending_by_merchant,
    spending_by_year_week,
    top_spending_category,
    total_spending,
    unique_transactions,
)


st.set_page_config(page_title="Personal Expense Analyzer", layout="wide")

CHART_HEIGHT = 390


def style_chart(chart, color: str) -> None:
    """Apply a consistent, readable presentation style to dashboard charts."""
    chart.update_layout(
        height=CHART_HEIGHT,
        showlegend=False,
        font={"size": 14, "color": "#1E293B"},
        title={"font": {"size": 18, "color": "#0F172A"}, "x": 0.01},
        margin={"l": 16, "r": 16, "t": 56, "b": 16},
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        hoverlabel={"bgcolor": "#0F172A", "font_size": 13},
    )
    chart.update_traces(marker_color=color)
    chart.update_traces(line_color=color, selector={"type": "scatter"})
    chart.update_xaxes(showgrid=False, tickfont={"size": 13}, title_standoff=12)
    chart.update_yaxes(
        gridcolor="#E2E8F0",
        zerolinecolor="#CBD5E1",
        tickfont={"size": 13},
        title_standoff=12,
    )


st.title("Personal Expense Analyzer")
st.caption("Understand where your money goes with a clear view of your spending.")
uploader_column, _ = st.columns([2, 3])
with uploader_column:
    uploaded_file = st.file_uploader(
        "Upload a transaction CSV", type=["csv"], width="stretch"
    )

if uploaded_file is None:
    st.info("Upload a CSV file to get started.")
else:
    try:
        raw_data = pd.read_csv(uploaded_file)
        cleaned_data, quality = clean_expense_data(raw_data)
    except Exception as error:
        st.error(
            "We couldn't read or clean this CSV. Check the file and try again. "
            f"Details: {error}"
        )
    else:
        invalid_rows = quality["unusable_rows_removed"]
        if invalid_rows:
            row_word = "row was" if invalid_rows == 1 else "rows were"
            st.warning(
                f"{invalid_rows} invalid {row_word} excluded while cleaning the uploaded file."
            )

        if cleaned_data.empty:
            st.warning("No usable transactions were found in this CSV.")
        else:
            st.sidebar.header("Filters")

            first_date = cleaned_data["Date"].min().date()
            last_date = cleaned_data["Date"].max().date()
            selected_dates = st.sidebar.date_input(
                "Date range",
                value=(first_date, last_date),
                min_value=first_date,
                max_value=last_date,
            )

            categories = sorted(cleaned_data["Category"].unique().tolist())
            merchants = sorted(cleaned_data["Merchant"].unique().tolist())
            payment_methods = sorted(cleaned_data["Payment_Method"].unique().tolist())

            selected_categories = st.sidebar.multiselect(
                "Category", categories, default=categories
            )
            selected_merchants = st.sidebar.multiselect(
                "Merchant", merchants, default=merchants
            )
            selected_payment_methods = st.sidebar.multiselect(
                "Payment Method", payment_methods, default=payment_methods
            )

            filtered_data = cleaned_data.copy()

            # Streamlit returns a pair of dates for a complete range selection.
            if isinstance(selected_dates, (tuple, list)) and len(selected_dates) == 2:
                start_date, end_date = selected_dates
                filtered_data = filtered_data[
                    filtered_data["Date"].dt.date.between(start_date, end_date)
                ]
            else:
                filtered_data = filtered_data.iloc[0:0]

            filtered_data = filtered_data[
                filtered_data["Category"].isin(selected_categories)
                & filtered_data["Merchant"].isin(selected_merchants)
                & filtered_data["Payment_Method"].isin(selected_payment_methods)
            ]

            if filtered_data.empty:
                st.info("No transactions match the selected filters.")
            else:
                st.subheader("Spending at a glance")
                metric_columns = st.columns(5)
                metric_columns[0].metric(
                    "Total Spending", f"${total_spending(filtered_data):,.2f}"
                )
                metric_columns[1].metric(
                    "Unique Transactions", f"{unique_transactions(filtered_data):,}"
                )
                metric_columns[2].metric(
                    "Average Transaction Value",
                    f"${average_transaction_value(filtered_data):,.2f}",
                )
                category = top_spending_category(filtered_data)
                metric_columns[3].metric("Top Spending Category", category or "N/A")
                metric_columns[4].metric(
                    "Highest Single Transaction",
                    f"${highest_single_transaction(filtered_data):,.2f}",
                )

                overview_tab, analysis_tab, transactions_tab = st.tabs(
                    ["Overview", "Spending Analysis", "Transactions"]
                )

                with overview_tab:
                    category_column, date_column = st.columns(2)
                    with category_column:
                        category_data = (
                            spending_by_category(filtered_data)
                            .rename_axis("Category")
                            .reset_index(name="Amount")
                        )
                        category_chart = px.bar(
                            category_data,
                            x="Category",
                            y="Amount",
                            title="Spending by Category",
                            labels={
                                "Category": "Category",
                                "Amount": "Spending (USD)",
                            },
                        )
                        style_chart(category_chart, "#2563EB")
                        category_chart.update_yaxes(
                            tickprefix="$", tickformat=",.2f"
                        )
                        st.plotly_chart(category_chart, width="stretch")

                    with date_column:
                        date_data = (
                            spending_by_date(filtered_data)
                            .rename_axis("Date")
                            .reset_index(name="Amount")
                        )
                        date_chart = px.line(
                            date_data,
                            x="Date",
                            y="Amount",
                            markers=True,
                            title="Spending Over Time",
                            labels={"Date": "Date", "Amount": "Spending (USD)"},
                        )
                        style_chart(date_chart, "#0F766E")
                        date_chart.update_yaxes(tickprefix="$", tickformat=",.2f")
                        st.plotly_chart(date_chart, width="stretch")

                    _, day_type_column, _ = st.columns([1, 2, 1])
                    with day_type_column:
                        day_type_data = (
                            spending_by_day_type(filtered_data)
                            .rename_axis("Day_Type")
                            .reset_index(name="Amount")
                        )
                        day_type_chart = px.bar(
                            day_type_data,
                            x="Day_Type",
                            y="Amount",
                            title="Weekday vs Weekend Spending",
                            labels={
                                "Day_Type": "Day Type",
                                "Amount": "Spending (USD)",
                            },
                        )
                        style_chart(day_type_chart, "#7C3AED")
                        day_type_chart.update_yaxes(
                            tickprefix="$", tickformat=",.2f"
                        )
                        st.plotly_chart(day_type_chart, width="stretch")

                with analysis_tab:
                    week_data = (
                        spending_by_year_week(filtered_data)
                        .rename_axis("Year_Week")
                        .reset_index(name="Amount")
                    )
                    week_chart = px.bar(
                        week_data,
                        x="Year_Week",
                        y="Amount",
                        title="Weekly Spending",
                        labels={
                            "Year_Week": "ISO Year and Week",
                            "Amount": "Spending (USD)",
                        },
                    )
                    style_chart(week_chart, "#2563EB")
                    week_chart.update_yaxes(tickprefix="$", tickformat=",.2f")
                    st.plotly_chart(week_chart, width="stretch")

                    merchant_column, item_column = st.columns(2)
                    with merchant_column:
                        merchant_data = (
                            spending_by_merchant(filtered_data)
                            .head(10)
                            .rename_axis("Merchant")
                            .reset_index(name="Amount")
                        )
                        merchant_chart = px.bar(
                            merchant_data,
                            x="Amount",
                            y="Merchant",
                            orientation="h",
                            title="Top 10 Merchants by Spending",
                            labels={
                                "Merchant": "Merchant",
                                "Amount": "Spending (USD)",
                            },
                        )
                        style_chart(merchant_chart, "#0F766E")
                        merchant_chart.update_xaxes(
                            tickprefix="$", tickformat=",.2f"
                        )
                        merchant_chart.update_yaxes(autorange="reversed")
                        st.plotly_chart(merchant_chart, width="stretch")

                    with item_column:
                        item_data = (
                            spending_by_item(filtered_data)
                            .head(10)
                            .rename_axis("Item")
                            .reset_index(name="Amount")
                        )
                        item_chart = px.bar(
                            item_data,
                            x="Amount",
                            y="Item",
                            orientation="h",
                            title="Top 10 Items by Spending",
                            labels={"Item": "Item", "Amount": "Spending (USD)"},
                        )
                        style_chart(item_chart, "#D97706")
                        item_chart.update_xaxes(tickprefix="$", tickformat=",.2f")
                        item_chart.update_yaxes(autorange="reversed")
                        st.plotly_chart(item_chart, width="stretch")

                with transactions_tab:
                    st.subheader("Filtered transactions")
                    search_text = st.text_input(
                        "Search transactions",
                        placeholder="Merchant, item, category, or transaction ID",
                    )

                    searched_data = filtered_data
                    if search_text:
                        search_mask = pd.Series(False, index=filtered_data.index)
                        for column in [
                            "Merchant",
                            "Item",
                            "Category",
                            "Transaction_ID",
                        ]:
                            search_mask |= filtered_data[column].astype("string").str.contains(
                                search_text, case=False, na=False, regex=False
                            )
                        searched_data = filtered_data[search_mask]

                    if searched_data.empty:
                        st.info("No transactions match your search.")
                    else:
                        st.dataframe(
                            searched_data, hide_index=True, width="stretch"
                        )
