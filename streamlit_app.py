import pinotdb
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta


# Define a modern color palette
COLORS = {
    'primary': '#3E2723',  # Dark brown
    'secondary': '#8D6E63',  # Light brown
    'background': '#EFEBE9',  # Light beige
    'accent': ['#795548', '#A1887F', '#BCAAA4', '#D7CCC8', '#EFEBE9']  # Brown palette
}

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
    if df.empty:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', color=COLORS['primary'])
        ax.set_title('Average Price by Coffee Type', fontsize=12, 
                    fontweight='bold', color=COLORS['primary'])
        ax.axis('off')
        return fig
    
    coffee_price_avg = df.groupby('COFFEE_TYPES')['TOTAL_PRICE'].mean()
    fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
    bars = coffee_price_avg.plot(kind='bar', ax=ax, color=COLORS['accent'])
    
    ax.set_title('Average Price by Coffee Type', fontsize=12, 
                fontweight='bold', color=COLORS['primary'])
    ax.set_xlabel('Coffee Type', fontsize=10, color=COLORS['primary'])
    ax.set_ylabel('Average Price (฿)', fontsize=10, color=COLORS['primary'])
    ax.tick_params(axis='both', colors=COLORS['primary'], labelsize=8)
    plt.xticks(rotation=45)
    
    for i, v in enumerate(coffee_price_avg):
        ax.text(i, v, f'฿{v:.0f}', ha='center', va='bottom', color=COLORS['primary'])
    
    plt.tight_layout()
    return fig

def plot_quantity_distribution(df):
    if df.empty:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', color=COLORS['primary'])
        ax.set_title('Order Quantity Distribution', fontsize=12, 
                    fontweight='bold', color=COLORS['primary'])
        ax.axis('off')
        return fig
    
    fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
    sns.histplot(df['QUANTITY'], kde=True, color=COLORS['secondary'], ax=ax)
    
    ax.set_title('Order Quantity Distribution', fontsize=12, 
                fontweight='bold', color=COLORS['primary'])
    ax.set_xlabel('Quantity', fontsize=10, color=COLORS['primary'])
    ax.set_ylabel('Number of Orders', fontsize=10, color=COLORS['primary'])
    ax.tick_params(axis='both', colors=COLORS['primary'], labelsize=8)
    
    plt.tight_layout()
    return fig

def plot_order_status_distribution(df):
    if df.empty:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', color=COLORS['primary'])
        ax.set_title('Order Status Distribution', fontsize=12, 
                    fontweight='bold', color=COLORS['primary'])
        ax.axis('off')
        return fig
    
    status_count = df['STATUS'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
    wedges, texts, autotexts = ax.pie(status_count, labels=status_count.index, 
                                     autopct='%1.1f%%', startangle=90, 
                                     colors=COLORS['accent'])
    
    plt.setp(autotexts, size=8, weight="bold", color=COLORS['primary'])
    plt.setp(texts, size=8, color=COLORS['primary'])
    
    ax.set_title('Order Status Distribution', fontsize=12, 
                fontweight='bold', color=COLORS['primary'])
    return fig

def plot_order_count_by_coffee_type(df):
    if df.empty:
        fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
        ax.text(0.5, 0.5, 'No data available', 
                ha='center', va='center', color=COLORS['primary'])
        ax.set_title('Orders by Coffee Type', fontsize=12, 
                    fontweight='bold', color=COLORS['primary'])
        ax.axis('off')
        return fig
    
    coffee_order_count = df['COFFEE_TYPES'].value_counts()
    fig, ax = plt.subplots(figsize=(6, 4), facecolor=COLORS['background'])
    
    bars = coffee_order_count.plot(kind='bar', ax=ax, color=COLORS['accent'])
    
    ax.set_title('Orders by Coffee Type', fontsize=12, 
                fontweight='bold', color=COLORS['primary'])
    ax.set_xlabel('Coffee Type', fontsize=10, color=COLORS['primary'])
    ax.set_ylabel('Number of Orders', fontsize=10, color=COLORS['primary'])
    ax.tick_params(axis='both', colors=COLORS['primary'], labelsize=8)
    plt.xticks(rotation=45)
    
    for i, v in enumerate(coffee_order_count):
        ax.text(i, v, str(v), ha='center', va='bottom', color=COLORS['primary'])
    
    plt.tight_layout()
    return fig

def create_metric_card(title, value, delta=None):
    st.markdown(f"""
        <div style="
            background-color: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            text-align: center;
            height: 150px;">
            <h3 style="color: {COLORS['primary']}; margin-bottom: 10px;">{title}</h3>
            <h2 style="color: {COLORS['secondary']}; margin-bottom: 5px;">{value}</h2>
            {f'<p style="color: green; margin: 0;">↑ {delta}%</p>' if delta and delta > 0 else ''}
            {f'<p style="color: red; margin: 0;">↓ {delta}%</p>' if delta and delta < 0 else ''}
        </div>
    """, unsafe_allow_html=True)

def main():
    st.set_page_config(layout="wide", page_title="Coffee Shop Dashboard", page_icon="☕")
    
    # Custom CSS
    st.markdown("""
        <style>
        .main {
            background-color: #EFEBE9;
        }
        .stButton>button {
            background-color: #795548;
            color: white;
            border-radius: 5px;
            padding: 10px 20px;
            border: none;
        }
        .stSelectbox {
            color: #3E2723;
        }
        </style>
    """, unsafe_allow_html=True)

    # Header
    st.markdown("""
        <h1 style='text-align: center; color: #3E2723; padding: 20px 0;'>
            ☕ Coffee Shop Dashboard
        </h1>
    """, unsafe_allow_html=True)

    # Filters in a single row
    col1, col2, col3 = st.columns(3)
    with col1:
        selected_coffee_type = st.selectbox("Coffee Type", 
                                          ['All'] + ['Espresso', 'Cappuccino', 'Latte', 'Americano'])
    with col2:
        selected_date = st.date_input("Select Date", datetime.now())
    with col3:
        show_all_data = True  # Set default to True to show all data initially

    # Fetch data
    query = """
    SELECT ORDERID, USERID, ORDER_TIMESTAMP, COFFEE_TYPES, QUANTITY, TOTAL_PRICE, STATUS
    FROM COFFEECITY
    """
    
    df = get_data_from_pinot(query)
    
    if df is not None:
        df['ORDER_TIMESTAMP'] = pd.to_datetime(df['ORDER_TIMESTAMP'])
        
        # Apply coffee type filter if selected
        if selected_coffee_type != 'All':
            df = df[df['COFFEE_TYPES'] == selected_coffee_type]

        # Key Metrics
        metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)
        
        with metric_col1:
            total_orders = len(df)
            create_metric_card("Total Orders", total_orders)
            
        with metric_col2:
            total_revenue = df['TOTAL_PRICE'].sum()
            create_metric_card("Total Revenue", f"฿{total_revenue:,.0f}")
            
        with metric_col3:
            avg_order_value = df['TOTAL_PRICE'].mean()
            create_metric_card("Average Order Value", f"฿{avg_order_value:,.0f}")
            
        with metric_col4:
            total_items = df['QUANTITY'].sum()
            create_metric_card("Total Items Sold", total_items)

        # Charts
        st.markdown("<br>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        
        with col1:
            st.pyplot(plot_average_price_by_coffee_type(df))
            st.pyplot(plot_order_status_distribution(df))
            
        with col2:
            st.pyplot(plot_quantity_distribution(df))
            st.pyplot(plot_order_count_by_coffee_type(df))

        

if __name__ == "__main__":
    main()