import streamlit as st
import pandas as pd
import pydeck as pdk
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import geopandas as gpd
from shapely.geometry import box

# Set Streamlit page config
st.set_page_config(page_title="Dengue Surveillance - Rawalpindi (city)", layout="wide")

def load_data():
    file_path = "Confirmed Patients 2013-2025.xlsx"
    try:
        df = pd.read_excel(file_path, sheet_name="Confirmed Patients 2013-2025")
    except FileNotFoundError:
        st.error("❌ Data file not found. Please check the file path.")
        st.stop()

    df = df.dropna(subset=["Latitude", "Longitude"])
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["Gender_Label"] = df["Gender"].str.capitalize()
    return df

# Load data
df = load_data()

# Define bounds and filter early (before use)
lat_min, lat_max = 33.5, 33.8
lon_min, lon_max = 72.9, 73.2
rawalpindi_df = df[(df["Latitude"] >= lat_min) & (df["Latitude"] <= lat_max) &
                   (df["Longitude"] >= lon_min) & (df["Longitude"] <= lon_max)]

# Main title and subheader
st.title("🦟 Dengue Surveillance Dashboard - (2013–2025) - Rawalpindi (city)")

# Create two columns
col1, col2 = st.columns([0.5, 1.5])

with col1:
#    world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
    world = gpd.read_file("https://raw.githubusercontent.com/datasets/geo-countries/master/data/countries.geojson")

    pakistan = world[world.name == 'Pakistan']
    rawalpindi_bounds = box(72.95, 33.5, 73.15, 33.75)
    rawalpindi = gpd.GeoDataFrame({'name': ['Rawalpindi'], 'geometry': [rawalpindi_bounds]}, crs="EPSG:4326")

    fig, ax = plt.subplots(figsize=(5, 5))
    pakistan.boundary.plot(ax=ax, color='black', linewidth=1)
    rawalpindi.plot(ax=ax, color='green', alpha=0.6, edgecolor='black')
    x, y = rawalpindi_bounds.centroid.x, rawalpindi_bounds.centroid.y
    ax.text(x, y, 'Rawalpindi', fontsize=12, ha='center', va='center', color='black')
    ax.axis('off')
    plt.tight_layout()
    st.pyplot(fig)

with col2:
    st.markdown("## 🏙️ Rawalpindi City Info")
    
    st.markdown(
        """
        <div style='font-size:18px; line-height:1.8;'>
            <b>📍 Province:</b> Punjab<br>
            <b>📐 Estimated Area:</b> ~259 km²<br>
            <b>👥 Estimated Population:</b> ~2.1 million<br>
            <b>🏙️ Known For:</b> Twin city of Islamabad<br>
            <b>🦟 Total Dengue Cases (Geo-based, 2013–2025):</b> <span style='color:red; font-weight:bold;'>12,270</span>
        </div>
        """,
        unsafe_allow_html=True
    )


# Map
st.subheader("📍 Geolocation of Confirmed Cases (Rawalpindi) - Small Red Dots")
map_data = rawalpindi_df[["Latitude", "Longitude"]].rename(columns={"Latitude": "lat", "Longitude": "lon"})

st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/light-v9',
    initial_view_state=pdk.ViewState(
        latitude=map_data["lat"].mean(),
        longitude=map_data["lon"].mean(),
        zoom=11,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScatterplotLayer",
            data=map_data,
            get_position='[lon, lat]',
            get_color='[255, 0, 0, 160]',
            get_radius=20,
            pickable=False,
        )
    ]
))

# Gender and Age Charts
col1, col2 = st.columns(2)

with col1:
    st.subheader("🧑‍🧑 Gender Distribution (Rawalpindi)")
    st.bar_chart(rawalpindi_df["Gender_Label"].value_counts())

with col2:
    st.subheader("📊 Age Distribution (Rawalpindi)")
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.histplot(rawalpindi_df["Age"].dropna(), kde=True, bins=30, color='skyblue', edgecolor='black', ax=ax)
    ax.set_title("Age Distribution of Dengue Patients (Rawalpindi)", fontsize=16)
    ax.set_xlabel("Age", fontsize=12)
    ax.set_ylabel("Number of Patients", fontsize=12)
    ax.set_xticks(range(0, 101, 5))
    ax.set_xlim(0, 100)
    st.pyplot(fig)

# Raw Data
with st.expander("🔍 View Raw Data (Filtered to Rawalpindi)"):
    st.dataframe(rawalpindi_df)


st.markdown("## 🌐 Dengue Trends by Month and Age Group")

# Load the data
file_path = "Dengue Surveillance Data/Confirmed Patients 2013-2025.xlsx"
full_df = pd.read_excel(file_path, sheet_name="Confirmed Patients 2013-2025")

# Month order for plotting
month_order = ['January', 'February', 'March', 'April', 'May', 'June',
               'July', 'August', 'September', 'October', 'November', 'December']

# Create two columns
col1, col2 = st.columns(2)

# ======== First Plot: By Age Group ========
with col1:
    st.subheader("📊 Monthly Age Group Distribution ")
    
    trend_df = full_df.dropna(subset=["Year", "Month", "Age"])
    bins = [0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]
    labels = ['0–10', '11–20', '21–30', '31–40', '41–50', '51–60', '61–70', '71–80', '81–90', '91–100']
    trend_df["Age_Group"] = pd.cut(trend_df["Age"], bins=bins, labels=labels, right=False)
    
    grouped = trend_df.groupby(["Year", "Month", "Age_Group"]).size().reset_index(name="Patient Count")
    grouped['Patient Count'] = grouped['Patient Count'] / 1000  # Convert to thousands
    grouped['Month'] = pd.Categorical(grouped['Month'], categories=month_order, ordered=True)
    
    fig1, ax1 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=grouped, x="Month", y="Patient Count", hue="Age_Group", ci=None, ax=ax1)
    ax1.set_title("Dengue Cases by Month and Age Group (in Thousands)")
    ax1.set_xlabel("Month")
    ax1.set_ylabel("Patient Count (Thousands)")
    ax1.tick_params(axis='x', rotation=45)
    st.pyplot(fig1)

# ======== Second Plot: Total Monthly Trends ========
with col2:
    st.subheader("📊 Monthly Total Patient Distribution ")

    trend_df_monthly = full_df.dropna(subset=["Year", "Month"])
    monthly_trends = trend_df_monthly.groupby(["Year", "Month"]).size().reset_index(name="Patient Count")
    monthly_trends["Patient Count"] = monthly_trends["Patient Count"] / 1000
    monthly_trends['Month'] = pd.Categorical(monthly_trends['Month'], categories=month_order, ordered=True)

    fig2, ax2 = plt.subplots(figsize=(10, 5))
    sns.barplot(data=monthly_trends, x="Month", y="Patient Count", ci=None, ax=ax2)
    ax2.set_title("Total Dengue Cases by Month (2013-2025) - in Thousands")
    ax2.set_xlabel("Month")
    ax2.set_ylabel("Total Patient Count (Thousands)")
    ax2.tick_params(axis='x', rotation=45)
    st.pyplot(fig2)


# ======== Third Plot: Heatmap Year vs Month ========
st.subheader("🗓️ Heatmap: Year-wise Monthly Dengue Cases")

# Prepare data
heatmap_df = full_df.dropna(subset=["Year", "Month"])
heatmap_grouped = heatmap_df.groupby(["Year", "Month"]).size().reset_index(name="Patient Count")
heatmap_grouped["Month"] = pd.Categorical(heatmap_grouped["Month"], categories=month_order, ordered=True)
heatmap_pivot = heatmap_grouped.pivot(index="Year", columns="Month", values="Patient Count").fillna(0)

# Plot heatmap
fig_heatmap, ax_heatmap = plt.subplots(figsize=(8, 5))
sns.heatmap(heatmap_pivot, annot=True, fmt=".0f", cmap="Reds", linewidths=0.5, linecolor="gray")
ax_heatmap.set_title("Year-wise Monthly Dengue Cases Heatmap")
ax_heatmap.set_xlabel("Month")
ax_heatmap.set_ylabel("Year")
st.pyplot(fig_heatmap)


# 3D Scatter Plot
st.subheader("📊 3D Plot: Year, Month, Age Group vs Patient Count")
fig3d = px.scatter_3d(
    grouped,
    x="Year",
    y="Month",
    z="Age_Group",
    size="Patient Count",
    color="Age_Group",
    opacity=0.7,
    title="3D View of Dengue Cases by Age Group Over Time"
)
fig3d.update_layout(
    scene=dict(
        xaxis_title="Year",
        yaxis_title="Month",
        zaxis_title="Age Group"
    ),
    height=800
)
st.plotly_chart(fig3d)

footer = """
    <style>
        .footer {
            width: 100%;
            background-color: #f8f9fa;
            text-align: center;
            padding: 15px;
            font-size: 14px;
            font-weight: bold;
            color: #333;
            border-top: 1px solid #ddd;
            margin-top: 50px;
        }
    </style>
    <div class="footer">
        📢 <b>This analysis is for educational purposes only.</b><br>
        🏫 <b>Supervised by:</b> Dr. Valerie Odon, Strathclyde University, UK<br>
        💻 <b>Developed by:</b> Odon’s Lab, PhD Students<br>
        📌 <i>Note: All data used here is sourced from official government sources and is not publicly available.</i>
    </div>
"""

st.write("\n" * 20)

st.markdown(footer, unsafe_allow_html=True)



