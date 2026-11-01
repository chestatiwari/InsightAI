import pandas as pd
import plotly.express as px

def top_n_bar(df, cat_col, value_col, n=10):

    # Group data by category and calculate total value
    chart_data = df.groupby(cat_col, as_index=False)[value_col].sum()

    # Sort values from highest to lowest
    chart_data = chart_data.sort_values(value_col, ascending=False)

    # Select only the top n categories
    chart_data = chart_data.head(n)

    # Create horizontal bar chart
    fig = px.bar(
        chart_data,
        x=value_col,
        y=cat_col,
        orientation="h",
        title=f"Top {n} {cat_col} by {value_col}"
    )

    return fig

def trend_line(df, date_col, value_col):

    # Make a separate copy of the required columns
    chart_data = df[[date_col, value_col]].copy()

    # Convert the date column into proper date format
    chart_data[date_col] = pd.to_datetime(
        chart_data[date_col], errors="coerce"
    )

    # Remove rows where the date is invalid
    chart_data = chart_data.dropna(subset=[date_col])

    # Convert every date into its corresponding month
    chart_data[date_col] = (
        chart_data[date_col].dt.to_period("M").dt.to_timestamp()
    )

    # Group by month and calculate total value
    chart_data = chart_data.groupby(
        date_col, as_index=False
    )[value_col].sum()

    # Create line chart
    fig = px.line(
        chart_data,
        x=date_col,
        y=value_col,
        markers=True,
        title=f"Monthly {value_col} Trend"
    )

    return fig

def scatter(df, x_col, y_col):

    # Create scatter plot
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        opacity=0.5,
        title=f"{y_col} vs {x_col}"
    )

    return fig

def histogram(df, col):

    # Create histogram
    fig = px.histogram(
        df,
        x=col,
        title=f"Distribution of {col}"
    )

    return fig