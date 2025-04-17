import streamlit as st
import pandas as pd
import plotly.express as px
import os
import asyncio
import json
from datetime import datetime
from browser_tool.agent import use_browser

# Set page configuration
st.set_page_config(
    page_title="ThinkSmart Internal ATS",
    page_icon="👨‍💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Initialize session state variables
if 'applications' not in st.session_state:
    st.session_state.applications = []
if 'last_check' not in st.session_state:
    st.session_state.last_check = None
if 'is_checking' not in st.session_state:
    st.session_state.is_checking = False
if 'cloudflare_message' not in st.session_state:
    st.session_state.cloudflare_message = False

# Function to check for new applications
async def check_new_applications():
    st.session_state.is_checking = True
    st.session_state.cloudflare_message = False
    try:
        # Use the browser tool to check Indeed employer dashboard
        task = "Check the Indeed employer dashboard for new applications and return them in JSON format with fields: name, position, date, status, experience, skills"
        result = await use_browser(task)
        
        # Parse the result and update applications
        try:
            new_apps = json.loads(result)
            if isinstance(new_apps, list):
                st.session_state.applications.extend(new_apps)
                st.session_state.last_check = datetime.now()
        except json.JSONDecodeError:
            st.error("Failed to parse application data")
    except Exception as e:
        st.error(f"Error checking for new applications: {str(e)}")
    finally:
        st.session_state.is_checking = False

# Sidebar
with st.sidebar:
    st.title("ThinkSmart Internal ATS")
    st.write("---")
    
    # Last check time
    if st.session_state.last_check:
        st.write(f"Last checked: {st.session_state.last_check.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for new applications button
    if st.button("Check for New Applications", disabled=st.session_state.is_checking):
        st.session_state.cloudflare_message = True
        asyncio.run(check_new_applications())
    
    # Cloudflare verification message
    if st.session_state.cloudflare_message:
        st.info("If you encounter a Cloudflare verification, please complete it in the browser window that opens. The system will continue automatically after verification.")
    
    # Filters
    st.write("---")
    st.subheader("Filters")
    
    # Status filter
    if st.session_state.applications:
        statuses = list(set(app.get('status', 'Unknown') for app in st.session_state.applications))
        selected_status = st.multiselect("Status", statuses, default=statuses)
    else:
        selected_status = []
    
    # Position filter
    if st.session_state.applications:
        positions = list(set(app.get('position', 'Unknown') for app in st.session_state.applications))
        selected_position = st.multiselect("Position", positions, default=positions)
    else:
        selected_position = []

# Main content
st.title("Application Dashboard")

# Filter applications
filtered_applications = st.session_state.applications
if selected_status:
    filtered_applications = [app for app in filtered_applications if app.get('status') in selected_status]
if selected_position:
    filtered_applications = [app for app in filtered_applications if app.get('position') in selected_position]

# Display applications
if filtered_applications:
    # Convert to DataFrame for easier display
    df = pd.DataFrame(filtered_applications)
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Applications", len(filtered_applications))
    with col2:
        st.metric("New Applications", len([app for app in filtered_applications if app.get('status') == 'New']))
    with col3:
        st.metric("Positions", len(set(app.get('position') for app in filtered_applications)))
    
    # Display applications table
    st.subheader("Applications")
    st.dataframe(df, use_container_width=True)
    
    # Visualizations
    col1, col2 = st.columns(2)
    
    with col1:
        # Applications by status
        status_counts = df['status'].value_counts()
        fig_status = px.pie(values=status_counts.values, names=status_counts.index, title="Applications by Status")
        st.plotly_chart(fig_status, use_container_width=True)
    
    with col2:
        # Applications by position
        position_counts = df['position'].value_counts()
        fig_position = px.bar(x=position_counts.index, y=position_counts.values, title="Applications by Position")
        st.plotly_chart(fig_position, use_container_width=True)
else:
    st.info("No applications found. Click 'Check for New Applications' to fetch data.") 