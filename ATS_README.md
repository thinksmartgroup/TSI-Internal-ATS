# ThinkSmart Internal ATS Dashboard

This dashboard provides a visual interface for managing job applications from Indeed. It automatically fetches application data from the Indeed employer dashboard and presents it in an easy-to-use format.

## Features

- **Real-time Application Tracking**: Automatically fetches new applications from Indeed
- **Visual Analytics**: Provides charts and metrics for application status and positions
- **Filtering**: Filter applications by status and position
- **Cloudflare Handling**: Automatically detects and handles Cloudflare verification
- **Voice Commands**: Use voice commands to interact with the dashboard (coming soon)

## Setup

### Prerequisites
- Python 3.11 or later
- Google Gemini API key

### Installation Steps

1. **Clone the repository:**
   ```sh
   git clone https://github.com/your-org/TSI-Internal-ATS.git
   cd TSI-Internal-ATS
   ```

2. **Create a virtual environment:**
   ```sh
   python3 -m venv .venv
   ```

3. **Activate the virtual environment:**
   - **Linux/macOS:**
     ```sh
     source .venv/bin/activate
     ```
   - **Windows:**
     ```sh
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```

5. **Set up environment variables:**
   - Copy `.env.sample` to `.env`
   - Fill in your API keys

6. **Run the Streamlit app:**
   ```sh
   streamlit run app.py
   ```

## Usage

1. **View Applications:**
   - The dashboard displays all applications fetched from Indeed
   - Use the sidebar filters to filter by status or position

2. **Check for New Applications:**
   - Click the "Check for New Applications" button in the sidebar to fetch the latest applications
   - If a Cloudflare verification appears, complete it in the browser window
   - The system will automatically continue after verification

3. **View Analytics:**
   - The dashboard provides visual analytics on application status and positions

## Troubleshooting

- **Authentication Issues:**
  - Check that your Google Gemini API key is valid

- **Cloudflare Verification:**
  - If you encounter a Cloudflare verification, complete it in the browser window
  - The system will wait for up to 5 minutes for verification to complete
  - If verification fails, try again later

- **Data Not Loading:**
  - Check your internet connection
  - Verify that the Indeed employer dashboard is accessible

## License

This project is proprietary and confidential. Unauthorized copying, distribution, or use is strictly prohibited. 