import streamlit as st
import pandas as pd
import plotly.express as px
import json
import random
from datetime import datetime, timedelta

# Set page configuration
st.set_page_config(
    page_title="ThinkSmart Internal ATS (Mock Data)",
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

# Function to generate mock applications
def generate_mock_applications(count=5):
    """Generate mock application data for testing"""
    positions = ["Software Engineer", "Data Scientist", "Product Manager", "UX Designer", "DevOps Engineer"]
    statuses = ["New", "Reviewed", "Interviewed", "Rejected", "Hired"]
    skills_list = [
        ["Python", "JavaScript", "React", "Node.js", "AWS"],
        ["Python", "R", "SQL", "Machine Learning", "Data Visualization"],
        ["Product Strategy", "Agile", "User Research", "Roadmap Planning", "Stakeholder Management"],
        ["Figma", "Adobe XD", "User Research", "Prototyping", "UI/UX Design"],
        ["Linux", "Docker", "Kubernetes", "CI/CD", "AWS"]
    ]
    
    applications = []
    for i in range(count):
        position = random.choice(positions)
        position_index = positions.index(position)
        skills = random.sample(skills_list[position_index], 3)
        
        application = {
            "name": f"Applicant {i+1}",
            "position": position,
            "date": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d"),
            "status": random.choice(statuses),
            "experience": random.randint(1, 10),
            "skills": skills
        }
        applications.append(application)
    
    return applications

# Function to check for new applications (mock)
def check_new_applications():
    st.session_state.is_checking = True
    try:
        # Generate mock applications
        new_apps = generate_mock_applications(random.randint(1, 3))
        st.session_state.applications.extend(new_apps)
        st.session_state.last_check = datetime.now()
    except Exception as e:
        st.error(f"Error generating mock applications: {str(e)}")
    finally:
        st.session_state.is_checking = False

# Sidebar
with st.sidebar:
    st.title("ThinkSmart Internal ATS (Mock Data)")
    st.write("---")
    
    # Last check time
    if st.session_state.last_check:
        st.write(f"Last checked: {st.session_state.last_check.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Check for new applications button
    if st.button("Generate Mock Applications", disabled=st.session_state.is_checking):
        check_new_applications()
    
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
st.title("Application Dashboard (Mock Data)")

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
    st.info("No applications found. Click 'Generate Mock Applications' to create sample data.") 