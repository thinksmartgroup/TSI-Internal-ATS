import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

st.set_page_config(page_title="TSI Employer ATS", layout="wide")

# Setup Google Sheets
def setup_google_sheets():
    scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

# Load data and enforce headers
def load_data():
    client = setup_google_sheets()
    sheet = client.open("TSI_ATS_Data")

    # Candidates
    candidates_ws = sheet.worksheet("Candidates")
    candidates_raw = candidates_ws.get_all_values()
    candidates = pd.DataFrame(candidates_raw[1:], columns=candidates_raw[0])

    # Jobs
    jobs_ws = sheet.worksheet("Jobs")
    jobs_raw = jobs_ws.get_all_values()
    jobs = pd.DataFrame(jobs_raw[1:], columns=jobs_raw[0])

    return candidates, jobs

# Save new candidate
def save_candidate(new_candidate):
    client = setup_google_sheets()
    worksheet = client.open("TSI_ATS_Data").worksheet("Candidates")
    worksheet.append_row(new_candidate)

# Save new job
def save_job(new_job):
    client = setup_google_sheets()
    worksheet = client.open("TSI_ATS_Data").worksheet("Jobs")
    worksheet.append_row(new_job)

# ---- UI ----
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Dashboard", "Candidates", "Jobs", "TSI Recruiter"])
st.sidebar.markdown("[Switch to Candidate Portal](http://localhost:8502)")

# Load data
candidates, jobs = load_data()

# ---- Pages ----
if page == "Dashboard":
    st.title("Employer Dashboard")
    st.metric("Total Candidates", len(candidates))
    
    try:
        st.metric("Open Jobs", len(jobs[jobs["Status"] == "Open"]))
    except KeyError:
        st.warning("Missing 'Status' column in Jobs sheet.")

elif page == "Candidates":
    st.title("Manage Candidates")
    st.dataframe(candidates)

    with st.expander("Add New Candidate"):
        with st.form("add_candidate_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email")
            phone = st.text_input("Phone Number")
            applied_jobs = st.multiselect("Applied Jobs", jobs["Title"].tolist())
            status = st.selectbox("Status", ["New", "In Review", "Interview", "Offer", "Hired", "Rejected"])
            skills = st.text_input("Skills")
            experience = st.number_input("Years of Experience", min_value=0)

            if st.form_submit_button("Submit"):
                new_candidate = [
                    str(datetime.now().timestamp()),
                    name, email, phone, status, ", ".join(applied_jobs), skills, str(experience)
                ]
                save_candidate(new_candidate)
                st.success("Candidate added successfully!")

elif page == "Jobs":
    st.title("Manage Jobs")
    st.dataframe(jobs)

    with st.expander("Add New Job"):
        with st.form("add_job_form"):
            title = st.text_input("Job Title")
            department = st.selectbox("Department", ["Engineering", "Sales", "Marketing", "HR", "Finance"])
            description = st.text_area("Job Description")
            status = st.selectbox("Status", ["Open", "Closed", "On Hold"])
            open_date = st.date_input("Open Date")
            close_date = st.date_input("Close Date")

            if st.form_submit_button("Add Job"):
                new_job = [
                    str(datetime.now().timestamp()),
                    title, department, description, status,
                    open_date.strftime("%Y-%m-%d"),
                    close_date.strftime("%Y-%m-%d")
                ]
                save_job(new_job)
                st.success("Job posted successfully!")

elif page == "TSI Recruiter":
    st.title("TSI Recruiter - AI Assistant")

    query = st.chat_input("Ask anything about candidates or jobs...")
    if query:
        st.chat_message("user").write(query)

        st.chat_message("assistant").write("Thinking...")

        if "top candidates" in query.lower():
            top = candidates.sort_values(by="Experience", ascending=False).head(3)
            st.chat_message("assistant").write(top[["Name", "Experience", "Skills"]].to_markdown())
        elif "open jobs" in query.lower():
            if "Description" not in jobs.columns:
                st.chat_message("assistant").write("Please add the 'Description' column to the Jobs sheet.")
            else:
                open_jobs = jobs[jobs["Status"] == "Open"]
                st.chat_message("assistant").write(open_jobs[["Title", "Description", "Open Date"]].to_markdown())
        else:
            st.chat_message("assistant").write("""
                I can help you find candidates or jobs. Try:
                - Show top candidates
                - List open jobs
            """)
