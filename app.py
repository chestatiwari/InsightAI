
import streamlit as st
import pandas as pd

from analysis import load_csv, profile


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
    st.write(
        "Business KPIs and charts will be added here."
    )

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
