
import pandas as pd
from pandas.errors import EmptyDataError


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