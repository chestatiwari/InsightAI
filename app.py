
import streamlit as st
import pandas as pd

from analysis import guess_column, load_csv, profile, kpis

# 1. Configure the page
st.set_page_config(
    page_title="InsightAI",
    layout="wide"
)

# 2. Display the app title and description
st.title("InsightAI - Business Analytics Copilot")
st.write("Upload a CSV file to explore your business data.")

# 3. Allow the user to upload a CSV file
uploaded_file = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

# 4. Load a new file when its filename changes
if uploaded_file is not None:
    current_filename = st.session_state.get("filename")

    if current_filename != uploaded_file.name:
        try:
            # Use our function from analysis.py to read the file
            df = load_csv(uploaded_file)

            # Save the data and filename across app reruns
            st.session_state["df"] = df
            st.session_state["filename"] = uploaded_file.name

        except ValueError as e:
            # Show a helpful message for known file problems
            st.session_state.pop("df", None)
            st.session_state.pop("filename", None)
            st.error(str(e))
            st.stop()

        except Exception:
            # Handle unexpected file-reading problems
            st.session_state.pop("df", None)
            st.session_state.pop("filename", None)
            st.error(
                "Could not read this file. Is it a valid CSV?"
            )
            st.stop()

# 5. Stop if no usable dataset is available
if "df" not in st.session_state:
    st.info("Upload a CSV file to begin.")
    st.stop()

# 6. Retrieve the saved dataset
df = st.session_state["df"]

st.caption(
    f"Current file: {st.session_state['filename']}"
)

# 6A. Let the user map dataset columns
columns = df.columns.tolist()

if not columns:
    st.error("The uploaded dataset has no columns.")
    st.stop()

with st.sidebar:
    st.header("Column Mapping")

    # Guess the likely columns automatically
    sales_guess = guess_column(
        df, ["sales", "revenue", "amount"]
    )
    profit_guess = guess_column(
        df, ["profit"]
    )
    order_guess = guess_column(
        df, ["order id", "order number"]
    )
    date_guess = guess_column(
        df, ["order date", "date"]
    )
    customer_guess = guess_column(
        df, ["customer name", "customer"]
    )

    # Required Sales column
    sales_col = st.selectbox(
        "Sales column",
        columns,
        index=columns.index(sales_guess)
        if sales_guess in columns else 0,
        key="sales_col"
    )

    # Optional columns: None is available as a choice
    profit_options = ["None"] + columns
    profit_col = st.selectbox(
        "Profit column (optional)",
        profit_options,
        index=(
            profit_options.index(profit_guess)
            if profit_guess in columns else 0
        ),
        key="profit_col"
    )

    order_options = ["None"] + columns
    order_col = st.selectbox(
        "Order ID column (optional)",
        order_options,
        index=(
            order_options.index(order_guess)
            if order_guess in columns else 0
        ),
        key="order_col"
    )

    date_options = ["None"] + columns
    date_col = st.selectbox(
        "Date column (optional)",
        date_options,
        index=(
            date_options.index(date_guess)
            if date_guess in columns else 0
        ),
        key="date_col"
    )

    customer_options = ["None"] + columns
    customer_col = st.selectbox(
        "Customer column (optional)",
        customer_options,
        index=(
            customer_options.index(customer_guess)
            if customer_guess in columns else 0
        ),
        key="customer_col"
    )


# 7. Create four tabs
tab1, tab2, tab3, tab4 = st.tabs(
    ["Overview", "Dashboard", "Ask", "Customers"]
)

# 8. Overview tab
with tab1:
    st.header("Dataset Overview")

    # Generate the data quality report
    report = profile(df)

    # Create four columns for summary metrics
    col1, col2, col3, col4 = st.columns(4)

    # Display the key dataset metrics
    col1.metric("Rows", report["rows"])
    col2.metric("Columns", report["cols"])
    col3.metric("Duplicate Rows", report["duplicates"])

    # Calculate overall missing-value percentage
    total_cells = df.size
    missing_cells = df.isna().sum().sum()
    missing_percent = (missing_cells / total_cells) * 100

    col4.metric("Missing Values", f"{missing_percent:.1f}%")

    
    # Show business KPIs in the Overview tab
    overview_metrics = kpis(
        df,
        sales_col,
        profit_col,
        order_col,
        date_col
    )

    st.subheader("Business KPIs")

    overview_cards = [
        ("Total Sales", overview_metrics["total_sales"], "currency"),
        ("Total Profit", overview_metrics["total_profit"], "currency"),
        ("Profit Margin", overview_metrics["margin_percent"], "percent"),
        ("Number of Orders", overview_metrics["number_of_orders"], "integer"),
        ("Average Order Value", overview_metrics["aov"], "currency"),
        ("Monthly Sales Growth", overview_metrics["growth_percent"], "percent")
    ]

    available_overview_cards = [
        card for card in overview_cards
        if card[1] is not None
        and not (
            card[0] in ["Total Profit", "Profit Margin"]
            and profit_col == "None"
        )
        and not (
            card[0] == "Monthly Sales Growth"
            and date_col == "None"
        )
    ]

    for start in range(0, len(available_overview_cards), 3):
        row_cards = available_overview_cards[start:start + 3]
        cols = st.columns(len(row_cards))

        for col, (label, value, kind) in zip(cols, row_cards):
            if kind == "currency":
                formatted_value = f"${value:,.2f}"
            elif kind == "percent":
                formatted_value = f"{value:.2f}%"
            else:
                formatted_value = f"{value:,}"

            col.metric(label, formatted_value)


    # Show missing-value analysis
    st.subheader("Missing Values by Column")
    st.dataframe(report["missing"], hide_index=True)

    # Warn about columns with more than 30% missing values
    high_missing = report["missing"][
        report["missing"]["Missing %"] > 30
    ]

    for _, row in high_missing.iterrows():
        st.warning(
            f"'{row['Column']}' has {row['Missing %']}% "
            "missing values."
        )

    # Show column types and statistics
    st.subheader("Column Information")
    st.dataframe(report["types"], hide_index=True)

    # Show potential outliers
    st.subheader("Potential Outliers (IQR Method)")
    st.dataframe(report["outliers"], hide_index=True)

    # Show statistical summary
    st.subheader("Statistical Summary")
    st.dataframe(report["describe"])

    st.subheader("First five rows")
    st.dataframe(df.head())


# 9. Dashboard tab
with tab2:
    st.header("Dashboard")

    metrics = kpis(
        df,
        sales_col,
        profit_col,
        order_col,
        date_col
    )

    # Display the KPIs that can be calculated
    cards = [
        ("Total Sales", metrics["total_sales"], "currency"),
        ("Total Profit", metrics["total_profit"], "currency"),
        ("Profit Margin", metrics["margin_percent"], "percent"),
        ("Number of Orders", metrics["number_of_orders"], "integer"),
        ("Average Order Value", metrics["aov"], "currency"),
        ("Monthly Sales Growth", metrics["growth_percent"], "percent"),
    ]

    available_cards = [
        card for card in cards
        if card[1] is not None
        and not (
            card[0] in ["Total Profit", "Profit Margin"]
            and profit_col == "None"
        )
        and not (
            card[0] == "Monthly Sales Growth"
            and date_col == "None"
        )
    ]

    # Show three KPI cards per row
    for start in range(0, len(available_cards), 3):
        row_cards = available_cards[start:start + 3]
        cols = st.columns(len(row_cards))

        for col, (label, value, kind) in zip(cols, row_cards):
            if kind == "currency":
                formatted_value = f"${value:,.2f}"
            elif kind == "percent":
                formatted_value = f"{value:.2f}%"
            else:
                formatted_value = f"{value:,}"

            col.metric(label, formatted_value)


# 10. Ask tab
with tab3:
    st.header("Ask InsightAI")
    st.write(
        "Natural-language data questions will be added here."
    )

# 11. Customers tab
with tab4:
    st.header("Customer Analysis")
    st.write(
        "Customer segmentation and insights will be added here."
    )
