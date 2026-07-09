import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
import os

# Set up Streamlit web app layout
st.set_page_config(page_title="Retail Inventory Optimization Portal", layout="wide")
st.title("📈 Retail Inventory Optimization & Time-Series Sales Tracker")

# --- FILE UPLOADER COMPONENT ---
st.sidebar.header("📁 Data Source Configuration")
uploaded_file = st.sidebar.file_uploader("Upload your Retail Inventory CSV file", type=["csv"])

# Load data dynamically based on user input or fallback file
@st.cache_data
def load_data(file_source):
    df = pd.read_csv(file_source)
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = None

# Logic to handle user upload vs default file
if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)
        st.sidebar.success("✅ Custom data loaded successfully!")
    except Exception as e:
        st.sidebar.error(f"❌ Error reading file. Please ensure columns match standard schema.")
elif os.path.exists("retail_inventory_sales_data.csv"):
    # Fallback to your default file if it exists in the GitHub repo
    df = load_data("retail_inventory_sales_data.csv")
    st.sidebar.info("💡 Running on default system dataset.")
else:
    # If there is no uploaded file AND no default file exists
    st.warning("👋 Welcome! Please upload a retail inventory CSV file in the sidebar to populate the optimization engine.")
    st.info("ℹ️ Your CSV file needs to contain at least these columns: `Date`, `Category`, `Units_Sold`, `Current_Stock_Level`, and `UnitPrice`.")

# --- MAIN APP LOGIC (Only runs if data is successfully loaded) ---
if df is not None:
    # Sidebar controls for warehouse managers
    st.sidebar.header("Filter Inventory Category")
    selected_category = st.sidebar.selectbox("Select Product Segment", df['Category'].unique())

    # Filter data based on choice
    category_df = df[df['Category'] == selected_category].sort_values('Date')

    # Business Analytics Calculations
    total_sold = category_df['Units_Sold'].sum()
    current_stock = category_df['Current_Stock_Level'].iloc[-1]
    avg_price = category_df['UnitPrice'].iloc[0]
    total_revenue = total_sold * avg_price

    # Metric Display Grid
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Volume Sold", f"{total_sold:,} Units")
    col2.metric("Total Revenue Generated", f"₹{total_revenue:,} INR")
    col3.metric("Current Warehouse Stock", f"{current_stock} Units")

    # Time-Series Demand Forecasting Section
    st.subheader(f"Historical Demand Trend & Predictive Forecasting: {selected_category}")

    # Feature engineering: converting dates to ordinal integers for a regression line calculation
    category_df['Date_Ordinal'] = category_df['Date'].apply(lambda x: x.toordinal())
    X = category_df[['Date_Ordinal']]
    y = category_df['Units_Sold']

    model = LinearRegression()
    model.fit(X, y)
    category_df['Forecast_Trend'] = model.predict(X)

    # Visualizing results
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(category_df['Date'], category_df['Units_Sold'], label="Actual Daily Sales Data", color="#1F4E78", alpha=0.6)
    ax.plot(category_df['Date'], category_df['Forecast_Trend'], label="Predictive Demand Forecast Trend", color="#C00000", linewidth=2.5)
    ax.set_ylabel("Units Demanded")
    ax.grid(True, linestyle="--", alpha=0.5)
    ax.legend()

    st.pyplot(fig)

    # Inventory Stockout Warning System Logic
    if current_stock < category_df['Units_Sold'].tail(7).mean() * 3:
        st.error(f"⚠️ STOCKOUT RISK WARNING: Current inventory levels for {selected_category} are insufficient to sustain demand over the next 72 hours. Trigger re-order sequence.")
    else:
        st.success(f"✅ INVENTORY SAFE: Warehouse optimization volumes are healthy for the current sales trend window.")
