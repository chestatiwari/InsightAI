
import streamlit as st
import pandas as pd

# Configure the page
st.set_page_config(
    page_title="InsightAI",
    layout="wide"
)

# Display the app title and description
st.title("InsightAI - Business Analytics Copilot")
st.write("Upload a CSV file to begin exploring your business data.")

# Allow the user to upload a CSV file
uploaded = st.file_uploader(
    "Upload a CSV file",
    type=["csv"]
)

# Process the file only after the user uploads it
if uploaded is not None:
    df = pd.read_csv(uploaded, encoding="latin-1")

    st.subheader("Dataset Preview")

    # Display the number of rows and columns
    st.write("Dataset shape (rows, columns):", df.shape)

    # Show the first five rows
    st.dataframe(df.head())


