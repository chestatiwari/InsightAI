
import pandas as pd
from pandas.errors import EmptyDataError


def guess_column(df, keywords):
    # Convert all keywords to lowercase
    keywords = [word.lower() for word in keywords]

    # Check each column name
    for column in df.columns:
        column_name = str(column).lower()

        # Check whether any keyword appears in the column name
        if any(word in column_name for word in keywords):
            return column

    # Return None if no column matches
    return None


def kpis(
    df,
    sales_col,
    profit_col=None,
    order_col=None,
    date_col=None
):
    # Convert selected columns safely to numbers
    sales = pd.to_numeric(
        df[sales_col], errors="coerce"
    )

    total_sales = sales.sum()

    # Calculate total profit if a profit column is selected
    total_profit = None
    if profit_col and profit_col != "None":
        profit = pd.to_numeric(
            df[profit_col], errors="coerce"
        )
        total_profit = profit.sum()

    # Calculate profit margin
    margin_percent = None
    if total_profit is not None and total_sales != 0:
        margin_percent = total_profit / total_sales * 100

    # Count distinct orders, or rows if no order column
    if order_col and order_col != "None":
        number_of_orders = df[order_col].nunique()
    else:
        number_of_orders = len(df)

    # Calculate Average Order Value
    aov = None
    if number_of_orders > 0:
        aov = total_sales / number_of_orders

    # Calculate monthly sales growth
    growth_percent = None

    if date_col and date_col != "None":
        dates = pd.to_datetime(
            df[date_col], errors="coerce"
        )

        monthly_data = pd.DataFrame({
            "Month": dates.dt.to_period("M"),
            "Sales": sales
        }).dropna(subset=["Month"])

        if not monthly_data.empty:
            monthly_sales = monthly_data.groupby(
                "Month"
            )["Sales"].sum()

            latest_month = monthly_sales.index.max()
            previous_month = latest_month - 1

            current_sales = monthly_sales.loc[latest_month]
            previous_sales = monthly_sales.get(
                previous_month, 0
            )

            if previous_sales != 0:
                growth_percent = (
                    (current_sales - previous_sales)
                    / abs(previous_sales)
                    * 100
                )

    return {
        "total_sales": total_sales,
        "total_profit": total_profit,
        "margin_percent": margin_percent,
        "number_of_orders": number_of_orders,
        "aov": aov,
        "growth_percent": growth_percent
    }


def load_csv(uploaded_file):
    # Try reading the CSV using Pandas' default encoding.
    try:
        df = pd.read_csv(uploaded_file)

    except UnicodeDecodeError:
        # Go back to the beginning before trying again.
        uploaded_file.seek(0)

        try:
            df = pd.read_csv(
                uploaded_file,
                encoding="latin-1"
            )
        except EmptyDataError:
            raise ValueError("The file is empty")

    except EmptyDataError:
        raise ValueError("The file is empty")

    # Check whether the file contains column names but no rows.
    if len(df) == 0:
        raise ValueError("The file has columns but no rows")

    # Return the successfully loaded DataFrame.
    return df

def profile(df):
    # Count the number of rows
    rows = df.shape[0]

    # Count the number of columns
    cols = df.shape[1]

    # Count fully duplicated rows
    duplicates = df.duplicated().sum()
    # Count missing values in each column
    missing_count = df.isna().sum()

    # Calculate the percentage of missing values
    missing_percent = (missing_count / len(df)) * 100
    
    # Create a table showing missing values
    missing = pd.DataFrame({
        "Column": df.columns,
        "Missing": missing_count.values,
        "Missing %": missing_percent.round(1).values
    })

    # Show columns with the most missing values first
    missing = missing.sort_values(
        by="Missing %",
        ascending=False
    )

    # Create a table with information about each column
    types = pd.DataFrame({
        "Column": df.columns,
        "Type": df.dtypes.astype(str).values,
        "Non-null": df.notna().sum().values,
        "Unique": df.nunique().values
    })

    # Select columns that contain numeric data
    numeric_df = df.select_dtypes(include="number")
    # Store the outlier results for each numeric column
    outlier_rows = []

    # Examine each numeric column one by one
    for column in numeric_df.columns:
        # Calculate the first and third quartiles
        q1 = numeric_df[column].quantile(0.25)
        q3 = numeric_df[column].quantile(0.75)

        # Calculate the interquartile range
        iqr = q3 - q1

        # Calculate the lower and upper limits
        lower = q1 - 1.5 * iqr
        upper = q3 + 1.5 * iqr
        # Count values outside the lower and upper limits
        outlier_count = (
            (numeric_df[column] < lower) |
            (numeric_df[column] > upper)
        ).sum()

        # Save the results for this column
        outlier_rows.append({
            "Column": column,
            "Q1": round(q1, 2),
            "Q3": round(q3, 2),
            "IQR": round(iqr, 2),
            "Lower": round(lower, 2),
            "Upper": round(upper, 2),
            "Outlier count": int(outlier_count)
        })
    
    # Create the final outlier table
    outliers = pd.DataFrame(
        outlier_rows,
        columns=[
            "Column", "Q1", "Q3", "IQR",
            "Lower", "Upper", "Outlier count"
        ]
    )

    # Return all the profiling results
    return {
        "rows": rows,
        "cols": cols,
        "duplicates": duplicates,
        "missing": missing,
        "types": types,
        "outliers": outliers,
        "describe": df.describe()
    }