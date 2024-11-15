import pinotdb
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta

# Define Earth-tone colors
earthtone_colors = ['#8C7853', '#B77A62', '#C49C6C', '#D3C0A7', '#A89F91']

def get_data_from_pinot(query):
    try:
        conn = pinotdb.connect(
            host='13.229.112.104',
            port=8099,
            path='/query/sql',
            scheme='http',
            timeout=500
        )
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"Error connecting: {e}")
        return None

def plot_average_price_by_coffee_type(df):
    coffee_price_avg = df.groupby('COFFEE_TYPES')['TOTAL_PRICE'].mean()
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#FFFBF0')
    
    # Assign Earth-tone colors to each bar
    colors = earthtone_colors[:len(coffee_price_avg)]
    coffee_price_avg.plot(kind='bar', ax=ax, color=colors)
    
    ax.set_title('Average Total Price by Coffee Type', fontsize=18, fontweight='bold', color='#5C4033')
    ax.set_xlabel('Coffee Type', fontsize=14, color='#5C4033')
    ax.set_ylabel('Average Total Price', fontsize=14, color='#5C4033')
    ax.tick_params(axis='both', colors='#5C4033', labelsize=12)
    return fig

def plot_quantity_distribution(df):
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#FFFBF0')
    ax = sns.histplot(df['QUANTITY'], kde=True, color='#8C7853')
    ax.set_title('Distribution of Order Quantity', fontsize=18, fontweight='bold', color='#5C4033')
    ax.set_xlabel('Quantity', fontsize=14, color='#5C4033')
    ax.set_ylabel('Frequency', fontsize=14, color='#5C4033')
    ax.tick_params(axis='both', colors='#5C4033', labelsize=12)
    return fig

def plot_order_status_distribution(df):
    status_count = df['STATUS'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#FFFBF0')
    ax.pie(status_count, labels=status_count.index, autopct='%1.1f%%', startangle=90, colors=['#8C7853', '#B8860B', '#DAA520'])
    ax.set_title('Order Status Distribution', fontsize=18, fontweight='bold', color='#5C4033')
    return fig

def plot_order_time_distribution(df):
    if df.empty:
        st.warning("ไม่มีข้อมูลสำหรับแสดงกราฟนี้")
        return None

    df['ORDER_TIMESTAMP'] = pd.to_datetime(df['ORDER_TIMESTAMP'])
    df['hour'] = df['ORDER_TIMESTAMP'].dt.hour
    df_grouped = df.groupby(['hour', 'COFFEE_TYPES']).size().reset_index(name='order_count')
    heatmap_data = df_grouped.pivot(index='hour', columns='COFFEE_TYPES', values='order_count').fillna(0)

    fig, ax = plt.subplots(figsize=(10, 8), facecolor='#FFFBF0')
    sns.heatmap(heatmap_data, annot=True, fmt="d", cmap="YlGnBu", cbar_kws={'label': 'Order Count'}, ax=ax)
    
    ax.set_title('Order Count Heatmap by Hour and Coffee Type', fontsize=18, fontweight='bold', color='#5C4033')
    ax.set_xlabel('Coffee Type', fontsize=14, color='#5C4033')
    ax.set_ylabel('Hour of Day', fontsize=14, color='#5C4033')
    ax.tick_params(axis='both', colors='#5C4033', labelsize=12)
    
    return fig

def plot_order_count_by_coffee_type(df):
    coffee_order_count = df['COFFEE_TYPES'].value_counts()
    fig, ax = plt.subplots(figsize=(8, 6), facecolor='#FFFBF0')
    
    # Assign Earth-tone colors to each bar
    colors = earthtone_colors[:len(coffee_order_count)]
    coffee_order_count.plot(kind='bar', ax=ax, color=colors)
    
    ax.set_title('Order Count by Coffee Type', fontsize=18, fontweight='bold', color='#5C4033')
    ax.set_xlabel('Coffee Type', fontsize=14, color='#5C4033')
    ax.set_ylabel('Number of Orders', fontsize=14, color='#5C4033')
    ax.tick_params(axis='both', colors='#5C4033', labelsize=12)
    return fig

def main():
    # Set Streamlit page configuration
    st.set_page_config(layout="wide", page_title="Coffee Shop Dashboard", page_icon=":coffee:")
    
    # Sidebar content
    st.sidebar.header('Coffee Shop Dashboard')
    st.sidebar.subheader('Latest Data & Insights')
    st.sidebar.markdown("Explore the latest trends in coffee orders and sales.")
    
    # Filter options in sidebar
    st.sidebar.subheader('Filter Options')
    selected_coffee_type = st.sidebar.selectbox("Select Coffee Type", ['All'] + ['Espresso', 'Cappuccino', 'Latte', 'Americano'])
    selected_date_range = st.sidebar.slider('Select Date Range', min_value=datetime(2022, 1, 1), max_value=datetime.now(),
                                           value=(datetime.now() - timedelta(days=1)), format="YYYY-MM-DD")

    query = """
    SELECT ORDERID, USERID, ORDER_TIMESTAMP, COFFEE_TYPES, QUANTITY, TOTAL_PRICE, STATUS
    FROM COFFEECITY
    """

    df = get_data_from_pinot(query)

    if df is not None:
        df['ORDER_TIMESTAMP'] = pd.to_datetime(df['ORDER_TIMESTAMP'])
        
        # Filter data based on selections
        if selected_coffee_type != 'All':
            df = df[df['COFFEE_TYPES'] == selected_coffee_type]
        df = df[df['ORDER_TIMESTAMP'] >= selected_date_range]

        last_24_hours = df[df['ORDER_TIMESTAMP'] >= (datetime.now() - timedelta(days=1))]

        # Main layout with columns
        st.title("Welcome to Coffee Shop Dashboard")
        st.markdown("This dashboard presents key insights into the coffee orders over the last 24 hours.")

        col1, col2 = st.columns(2)
        col3, col4 = st.columns(2)

        with col1:
            st.pyplot(plot_average_price_by_coffee_type(last_24_hours))

        with col2:
            st.pyplot(plot_quantity_distribution(last_24_hours))

        with col3:
            st.pyplot(plot_order_status_distribution(last_24_hours))

        with col4:
            st.pyplot(plot_order_count_by_coffee_type(last_24_hours))

        # Data Table Section in Sidebar
        st.sidebar.subheader('Recent Orders')
        st.sidebar.dataframe(last_24_hours[['ORDERID', 'USERID', 'COFFEE_TYPES', 'QUANTITY', 'TOTAL_PRICE', 'STATUS']])
    else:
        st.write("Failed to fetch data from the database.")

if __name__ == "__main__":
    main()
