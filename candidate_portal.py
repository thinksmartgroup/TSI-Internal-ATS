import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
from dotenv import load_dotenv
import os

load_dotenv()

st.set_page_config(page_title="TSI Candidate Portal", layout="centered")

# Setup Google Sheets
def setup_google_sheets():
    scope = [os.getenv('GSPREAD_SCOPES_FEEDS'), os.getenv('GSPREAD_SCOPES_DRIVE')]
    creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

# Load candidate info
def fetch_candidate_data(email):
    client = setup_google_sheets()
    sheet = client.open("TSI_ATS_Data").worksheet("Candidates")
    data = sheet.get_all_records()
    df = pd.DataFrame(data)
    return df[df["Email"].str.lower() == email.lower()]

# ---- UI ----
st.title("Welcome to TSI Candidate Portal")

st.markdown("Please enter your registered **Email** to view your application details:")

email = st.text_input("Email", placeholder="your.email@example.com")

if email:
    try:
        candidate_df = fetch_candidate_data(email)
        if not candidate_df.empty:
            candidate = candidate_df.iloc[0]
            st.success(f"Found candidate: {candidate['Name']}")
            st.write("### Application Summary")
            st.markdown(f"""
                - **Status:** {candidate['Status']}
                - **Applied Jobs:** {candidate['Applied Jobs']}
                - **Skills:** {candidate['Skills']}
                - **Experience:** {candidate['Experience']} years
            """)
            st.markdown("We’ll notify you as your application progresses!")
        else:
            st.warning("No candidate found with that email.")
    except Exception as e:
        st.error(f"Error: {str(e)}")

st.markdown("---")
st.markdown("[Switch to Employer Portal](http://localhost:8501)")
