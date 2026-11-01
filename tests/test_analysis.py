
import pandas as pd
import pytest
from io import StringIO
from analysis import kpis, profile, load_csv, rfm


def create_tiny_data():
    data = {
        "Order ID": [
            "O1", "O1", "O2", "O3", "O4",
            "O5", "O6", "O7", "O8", "O8"
        ],
        "Order Date": [
            "2024-01-05", "2024-01-05", "2024-01-20",
            "2024-02-03", "2024-02-14", "2024-02-28",
            "2024-03-10", "2024-03-15", "2024-03-30",
            "2024-03-30"
        ],
        "Customer ID": [
            "C1", "C1", "C2", "C3", "C1",
            "C4", "C2", "C5", "C3", "C3"
        ],
        "Region": [
            "West", "West", "East", "West", "West",
            "South", "East", "South", "West", "West"
        ],
        "Category": [
            "Furniture", "Technology", "Furniture",
            "Office Supplies", "Technology", "Furniture",
            "Office Supplies", "Technology", "Furniture",
            "Furniture"
        ],
        "Sales": [
            100, 200, 150, 50, 300,
            120, 80, 250, 90, 90
        ],
        "Profit": [
            20, 50, -10, 10, 90,
            None, 8, 75, -5, -5
        ]
    }

    return pd.DataFrame(data)


def test_kpis():
    df = create_tiny_data()

    result = kpis(
        df,
        sales_col="Sales",
        profit_col="Profit",
        order_col="Order ID"
    )

    assert result["total_sales"] == 1430
    assert result["total_profit"] == 233
    assert result["number_of_orders"] == 8
    assert result["aov"] == 178.75


def test_profile():
    df = create_tiny_data()

    result = profile(df)

    assert result["rows"] == 10
    assert result["cols"] == 7
    assert result["duplicates"] == 1

    missing_profit = result["missing"].loc[
        result["missing"]["Column"] == "Profit",
        "Missing"
    ].iloc[0]

    assert missing_profit == 1

def test_load_csv():
    with open("data/tiny.csv", "r") as file:
        df = load_csv(file)

    assert len(df) == 10
    assert len(df.columns) == 7


def test_load_empty_csv():
    empty_file = StringIO("")

    with pytest.raises(ValueError, match="The file is empty"):
        load_csv(empty_file)


def test_load_csv_with_no_rows():
    empty_rows_file = StringIO("Name,Age\n")

    with pytest.raises(
        ValueError,
        match="The file has columns but no rows"
    ):
        load_csv(empty_rows_file)

def test_rfm():
    df = create_tiny_data()

    result = rfm(
        df,
        customer_col="Customer ID",
        date_col="Order Date",
        amount_col="Sales",
        invoice_col="Order ID"
    )

    # Check that RFM results are generated
    assert result is not None

    # Check that all 5 customers are included
    assert len(result) == 5

    # Check that required columns exist
    required_columns = [
        "Recency",
        "Frequency",
        "Monetary",
        "R_score",
        "F_score",
        "M_score",
        "RFM_score",
        "Segment"
    ]

    for column in required_columns:
        assert column in result.columns

    # Check customer C1's frequency
    customer_c1 = result[
        result["Customer ID"] == "C1"
    ].iloc[0]

    assert customer_c1["Frequency"] == 2

    # Check customer C3's recency
    customer_c3 = result[
        result["Customer ID"] == "C3"
    ].iloc[0]

    assert customer_c3["Recency"] == 1

    # Check that individual RFM scores are between 1 and 5
    for column in ["R_score", "F_score", "M_score"]:
        assert result[column].between(1, 5).all()

    # Check that total score equals the sum of individual scores
    assert (
        result["RFM_score"]
        == result["R_score"] + result["F_score"] + result["M_score"]
    ).all()

    # Check that every customer has a valid segment
    valid_segments = ["Champions", "Loyal", "Potential", "At Risk"]

    assert result["Segment"].isin(valid_segments).all()
