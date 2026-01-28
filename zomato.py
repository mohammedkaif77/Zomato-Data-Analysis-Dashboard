import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt

# Set page config
st.set_page_config(page_title="Zomato Data Analysis Dashboard", layout="wide")

# Apply Custom Styles
st.markdown(
    """
    <style>
        /* Smooth Fade-in Animation */
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        .fade {
            animation: fadeIn 1.5s;
        }
        /* Custom Font */
        html, body, [class*="css"] {
            font-family: 'Poppins', sans-serif;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Ensure analysis state persists across reruns
if "analysis_started" not in st.session_state:
    st.session_state.analysis_started = False

# Show Welcome Page ONLY if analysis has NOT started
if not st.session_state.analysis_started:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image("zomato1.png", use_container_width=True)

    st.markdown("<h1 style='text-align: center;' class='fade'>🍽 Welcome to Zomato Data Analysis Dashboard</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center;'>🔍 Explore restaurant insights like never before!</p>", unsafe_allow_html=True)

    # Center the button properly using Streamlit columns
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2:
        if st.button("🚀 Let's Analyze!", key="start_analysis"):
            st.session_state.analysis_started = True
            st.rerun()

    st.stop()  # Prevents the rest of the script from running before clicking the button


# Loading Animation with Spinner
with st.spinner("🔄 Loading Data..."):
    @st.cache_data(ttl=600)
    def load_data():
        df = pd.read_csv("Zomato-data-multi-year.csv")
        df.columns = df.columns.str.strip()
        return df

    df = load_data()

# Sidebar Filters (Optimized)
st.sidebar.header("🎛 Advanced Filters")

unique_cities = df['city'].dropna().unique()
unique_types = df['listed_in(type)'].dropna().unique()

selected_cities = st.sidebar.multiselect("🏙 Select City", unique_cities, default=unique_cities, help="Filter restaurants by city")
selected_types = st.sidebar.multiselect("🍽 Select Restaurant Type", unique_types, default=unique_types, help="Choose the type of restaurant")
rating_range = st.sidebar.slider("⭐ Select Rating Range", float(df['rate'].min()), float(df['rate'].max()), (float(df['rate'].min()), float(df['rate'].max())), help="Set minimum and maximum rating")
cost_range = st.sidebar.slider("💰 Select Cost Range", float(df['approx_cost(for two people)'].min()), float(df['approx_cost(for two people)'].max()), 
                               (float(df['approx_cost(for two people)'].min()), float(df['approx_cost(for two people)'].max())), help="Set cost range for two people")
online_order_filter = st.sidebar.checkbox("🛒 Show Only Online Order Restaurants", value=False, help="Show restaurants that accept online orders")

if st.sidebar.button("🔄 Reset Filters"):
    st.session_state.clear()
    st.rerun()

# Apply Filters
df_filtered = df[(df['city'].isin(selected_cities)) & 
                 (df['listed_in(type)'].isin(selected_types)) & 
                 (df['rate'].between(*rating_range)) & 
                 (df['approx_cost(for two people)'].between(*cost_range))]

if online_order_filter:
    df_filtered = df_filtered[df_filtered['online_order'] == "Yes"]

if df_filtered.empty:
    st.warning("⚠ No data found. Try adjusting filters!")
else:
    with st.expander("📊 Key Insights", expanded=True):
        st.write(f"📝 **Total Restaurants Analyzed**: {df_filtered.shape[0]}")
        st.write(f"⭐ **Average Rating**: {df_filtered['rate'].mean():.2f}")
        st.write(f"💰 **Average Cost for Two People**: ₹{df_filtered['approx_cost(for two people)'].mean():.2f}")

    if 'year' in df.columns and df['year'].notna().sum() > 0:
        st.subheader("📈 Restaurant Growth Over Years")
        yearly_growth = df.groupby('year').size().reset_index(name='Restaurant Count')
        if len(yearly_growth) > 1:
            fig1 = px.line(yearly_growth, x='year', y='Restaurant Count', title="Growth of Restaurants Over the Years", markers=True, color_discrete_sequence=['#FF5733'])
            st.plotly_chart(fig1, use_container_width=True)

    st.subheader("💰 Cost vs. Rating Distribution")
    fig4 = px.scatter(df_filtered, x='approx_cost(for two people)', y='rate', size='votes', color='city', title="Cost vs. Rating Analysis", color_continuous_scale='viridis')
    st.plotly_chart(fig4, use_container_width=True)

    st.subheader("🔥 Enhanced Correlation Heatmap")
    heatmap_data = df_filtered[['rate', 'approx_cost(for two people)', 'votes']].corr()
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.heatmap(heatmap_data, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5, square=True, cbar_kws={'shrink': 0.8}, ax=ax)
    ax.set_title("Correlation Between Rating, Cost & Votes", fontsize=14)
    st.pyplot(fig)

    st.subheader("🍩 Restaurant Type Breakdown")
    type_counts = df_filtered['listed_in(type)'].value_counts().reset_index()
    type_counts.columns = ['Type', 'Count']
    fig5 = px.pie(type_counts, names='Type', values='Count', title="Restaurant Type Distribution", hole=0.35, color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig5, use_container_width=True)

    st.subheader("🏙 Top Cities by Restaurant Count")
    city_counts = df_filtered['city'].value_counts().reset_index()
    city_counts.columns = ['City', 'Count']
    fig6 = px.bar(city_counts, x='City', y='Count', title="Top Cities with Most Restaurants", color='City', text_auto=True)
    st.plotly_chart(fig6, use_container_width=True)

    st.subheader("📋 Top 10 Restaurants by Rating")
    top_restaurants = df_filtered[['city', 'rate', 'approx_cost(for two people)', 'votes']].sort_values(by=['rate', 'votes'], ascending=[False, False]).head(10)
    st.table(top_restaurants)