from pathlib import Path

import streamlit as st
import pandas as pd
import plotly.express as px

# # 1. Page Configuration (Modern Dark Theme Settings)
# st.set_page_config(page_title="LLMOps Cost & Performance Monitor", layout="wide")

# # Custom CSS for Premium Dark UI
# st.markdown("""
#     <style>
#     .main { background-color: #0F172A; color: #F8FAFC; }
#     div[data-testid="metric-container"] {
#         background-color: #1E293B;
#         border: 1px solid #334155;
#         padding: 15px;
#         border-radius: 10px;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # 2. Load Dataset
# @st.cache_data
# def load_data():
#     data_path = Path(__file__).with_name("llm_ops_dashboard_data.csv")
#     df = pd.read_csv(data_path)
#     df['timestamp'] = pd.to_datetime(df['timestamp'])
#     return df

# df = load_data()

# # 3. Sidebar Header & Filters (Interactive Department Slicer)
# st.sidebar.title("🛠️ LLMOps Settings")
# departments = ['All'] + list(df['department'].unique())
# selected_dept = st.sidebar.selectbox("Select Department Focus", departments)

# # Filter data dynamically
# if selected_dept != 'All':
#     filtered_df = df[df['department'] == selected_dept]
# else:
#     filtered_df = df

# # 4. Main Dashboard Header
# st.title("📊 LLMOps Cost & Performance Monitor")
# st.markdown("Real-time enterprise metrics tracking framework for frontier models.")
# st.markdown("---")

# # 5. Top KPI Cards Row
# col1, col2, col3, col4 = st.columns(4)

# total_spend = filtered_df['cost_usd'].sum()
# total_requests = len(filtered_df)
# avg_latency = filtered_df['latency_ms'].mean()
# error_rate = (len(filtered_df[filtered_df['status'] != 'Success']) / total_requests) * 100

# col1.metric("💰 Total API Spend", f"${total_spend:,.2f}")
# col2.metric("🔄 Total API Requests", f"{total_requests:,}")
# col3.metric("⚡ Avg Latency", f"{int(avg_latency)} ms")
# col4.metric("🚨 System Error Rate", f"{error_rate:.1f}%")

# st.markdown("<br>", unsafe_allow_html=True)

# # 6. Charts Layout Row 1
# chart_col1, chart_col2 = st.columns(2)

# with chart_col1:
#     st.subheader("Cost Distribution by AI Model")
#     fig_donut = px.pie(filtered_df, values='cost_usd', names='model_name', hole=0.5,
#                        color_discrete_sequence=['#8B5CF6', '#06B6D4', '#EC4899'])
#     fig_donut.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
#     st.plotly_chart(fig_donut, use_container_width=True)

# with chart_col2:
#     st.subheader("Department Spend Efficiency Split")
#     dept_cost = filtered_df.groupby('department')['cost_usd'].sum().reset_index()
#     fig_bar = px.bar(dept_cost, x='cost_usd', y='department', orientation='h',
#                      color_discrete_sequence=['#06B6D4'])
#     fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
#     st.plotly_chart(fig_bar, use_container_width=True)

# # 7. Charts Layout Row 2 (Timeline Graph)
# st.subheader("Hourly Latency Spikes Tracker (ms)")
# # Resample to hourly timeline for smoother chart mapping
# filtered_df['hour'] = filtered_df['timestamp'].dt.strftime('%m-%d %H:00')
# timeline_df = filtered_df.groupby('hour')['latency_ms'].mean().reset_index()

# fig_line = px.line(timeline_df, x='hour', y='latency_ms', markers=True,
#                    color_discrete_sequence=['#8B5CF6'])
# fig_line.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
# st.plotly_chart(fig_line, use_container_width=True)




# 1. Page Config with Pinterest/Dribbble UI proportions
st.set_page_config(page_title="Cloud LLMOps Hub", layout="wide", initial_sidebar_state="expanded")

# 2. Custom CSS to inject Glassmorphism borders and custom font grids
st.markdown("""
    <style>
    /* Main Background and fonts */
    .main { background-color: #0B0F19; color: #E2E8F0; font-family: 'Inter', sans-serif; }
    [data-testid="stSidebar"] { background-color: #111827 !important; border-right: 1px solid #1F2937; }
    
    /* Pinterest-style modern glass containers */
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #1F2937 0%, #111827 100%);
        border: 1px solid #374151;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMarkdownContainer"] h2 {
        color: #F3F4F6; font-weight: 600; letter-spacing: -0.025em;
    }
    </style>
""", unsafe_allow_html=True)

# 3. Load Data
@st.cache_data
def load_data():
    data_path = Path(__file__).with_name("llm_ops_dashboard_data.csv")
    df = pd.read_csv(data_path)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    return df

df = load_data()

# 4. Pinterest-style Navigation Menu (Multi-page Setup)
st.sidebar.markdown("<h2 style='color:#8B5CF6; margin-bottom:20px;'>🔮 NexaLLM Ops</h2>", unsafe_allow_html=True)
page = st.sidebar.radio("NAVIGATION", ["📊 Core Analytics", "⚡ Performance Audit", "📁 Raw Logs Explorer"])

st.sidebar.markdown("---")
# Global Department Slicer across tabs
departments = ['All Departments'] + list(df['department'].unique())
selected_dept = st.sidebar.selectbox("🎯 Department Scope", departments)

if selected_dept != 'All Departments':
    filtered_df = df[df['department'] == selected_dept].copy()
else:
    filtered_df = df.copy()

# ----------------- PAGE 1: CORE ANALYTICS -----------------
if page == "📊 Core Analytics":
    st.markdown("<h1 style='letter-spacing:-1px;'>Overview Analytics</h1>", unsafe_allow_html=True)
    st.markdown("Cost optimization and allocation framework.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern Layout Metric grids
    col1, col2, col3 = st.columns(3)
    total_spend = filtered_df['cost_usd'].sum()
    total_requests = len(filtered_df)
    active_models = filtered_df['model_name'].nunique()
    
    col1.metric("💰 Total Infrastructure Spend", f"${total_spend:,.2f}")
    col2.metric("🔄 Distributed Requests", f"{total_requests:,}")
    col3.metric("🤖 Deployed Frontier Models", f"{active_models} Active")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Grid Content
    g_col1, g_col2 = st.columns(2)
    with g_col1:
        st.markdown("### Cost Distribution share")
        fig_donut = px.pie(filtered_df, values='cost_usd', names='model_name', hole=0.6,
                           color_discrete_sequence=['#A78BFA', '#22D3EE', '#F472B6'])
        fig_donut.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', showlegend=True)
        st.plotly_chart(fig_donut, use_container_width=True)
        
    with g_col2:
        st.markdown("### Department Budget Consumption")
        dept_cost = filtered_df.groupby('department')['cost_usd'].sum().reset_index()
        fig_bar = px.bar(dept_cost, x='cost_usd', y='department', orientation='h',
                         color_discrete_sequence=['#22D3EE'])
        fig_bar.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_bar, use_container_width=True)

# ----------------- PAGE 2: PERFORMANCE AUDIT -----------------
elif page == "⚡ Performance Audit":
    st.markdown("<h1 style='letter-spacing:-1px;'>Telemetry & Performance</h1>", unsafe_allow_html=True)
    st.markdown("Latency distributions and system runtime stability diagnostics.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    avg_latency = filtered_df['latency_ms'].mean()
    error_rate = (len(filtered_df[filtered_df['status'] != 'Success']) / len(filtered_df)) * 100
    
    col1.metric("⚡ Cluster Mean Latency", f"{int(avg_latency)} ms")
    col2.metric("🚨 HTTP Gateway Error Rate", f"{error_rate:.2f}%")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("### Chronological Latency Spikes (Hourly)")
    filtered_df['hour'] = filtered_df['timestamp'].dt.strftime('%m-%d %H:00')
    timeline_df = filtered_df.groupby('hour')['latency_ms'].mean().reset_index()
    
    fig_line = px.line(timeline_df, x='hour', y='latency_ms', markers=True,
                       color_discrete_sequence=['#A78BFA'])
    fig_line.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
    st.plotly_chart(fig_line, use_container_width=True)

# ----------------- PAGE 3: RAW LOGS EXPLORER -----------------
elif page == "📁 Raw Logs Explorer":
    st.markdown("<h1 style='letter-spacing:-1px;'>Data Ledger Logs</h1>", unsafe_allow_html=True)
    st.markdown("Inspect or export production transactional tokens information directly.")
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Modern Interactive Data Table
    st.dataframe(filtered_df[['timestamp', 'user_id', 'model_name', 'cost_usd', 'latency_ms', 'status']], 
                 use_container_width=True, hide_index=True)
