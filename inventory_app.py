import pandas as pd
import numpy as np
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression

# Set up Streamlit web app layout
st.set_page_config(page_title="Retail Inventory Optimization Portal", layout="wide")
st.title("📈 Retail Inventory Optimization & Time-Series Sales Tracker")

# Load multi-year timeline records
@st.cache_data
def load_data():
    df = pd.read_csv("retail_inventory_sales_data.csv")
    df['Date'] = pd.to_datetime(df['Date'])
    return df

df = load_data()

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
