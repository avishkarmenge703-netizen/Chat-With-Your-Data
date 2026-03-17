import pandas as pd
import streamlit as st

@st.cache_data
def load_data(uploaded_file):
    """
    Load data from uploaded CSV or Excel file.
    Returns a pandas DataFrame and a status message.
    """
    if uploaded_file is None:
        return None, "No file uploaded."

    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file)
        else:
            return None, "Unsupported file type. Please upload CSV or Excel."

        if df.empty:
            return None, "The file is empty."

        return df, f"Successfully loaded {df.shape[0]} rows and {df.shape[1]} columns."

    except Exception as e:
        return None, f"Error loading file: {str(e)}"
