# TSI Internal ATS

A modern Applicant Tracking System (ATS) built with Streamlit for managing job applications, candidates, and interviews.

## Features

- **Dashboard**: Overview of candidates, jobs, and interviews
- **Candidate Management**: Track and manage candidate information
- **Job Posting**: Create and manage job postings
- **Interview Scheduling**: Schedule and track interviews
- **Analytics**: Visualize data with charts and graphs
- **AI Assistant**: Get insights and recommendations about candidates and jobs

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/TSI-Internal-ATS.git
   cd TSI-Internal-ATS
   ```

2. Create a virtual environment and activate it:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up Google Sheets integration:
   - Create a Google Cloud project
   - Enable the Google Sheets API
   - Create a service account and download the JSON key file
   - Rename the downloaded file to `credentials.json` and place it in the project root
   - Create a Google Sheet named "TSI_ATS_Data" with three worksheets: "Candidates", "Jobs", and "Interviews"

5. Configure environment variables:
   - Copy `.env.sample` to `.env`
   - Update the values in `.env` with your credentials

## Running the Application

Run the application with:
   ```bash
   streamlit run simple_dash.py
   ```

The application will open in your default web browser.

## Using the AI Assistant

The AI Assistant can help you analyze candidates and jobs. Try commands like:

- "Analyze candidate John Doe"
- "Analyze job Software Engineer"
- "Compare candidates John Doe Jane Smith"
- "Suggest jobs for John Doe"
- "Suggest candidates for Software Engineer"

## Troubleshooting

- If you encounter an error about missing files, make sure all required files are in place
- For Google Sheets integration issues, verify your credentials and API access
- If the application doesn't start, check your Python version and dependencies

## License

This project is licensed under the MIT License - see the LICENSE file for details.

