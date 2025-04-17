# Indeed Assistant

A chat-based assistant for managing job applications on Indeed.

## Overview

This project provides a chat-based interface for automating tasks on the Indeed employer dashboard. It allows you to:

- Log in to Indeed
- Open job posts
- Get applicants for jobs
- Send interview invites
- Update applicant statuses
- Search for jobs
- Create job posts

## Components

The project consists of the following components:

1. **Indeed Automation Module** (`browser_tool/indeed_automation.py`): Contains functions for interacting with the Indeed employer dashboard.
2. **Chat Interface** (`chat_interface.py`): Provides a natural language interface for the automation functions.
3. **Dashboard** (`dashboard.html`): A web-based interface for interacting with the assistant.
4. **API Server** (`api_server.py`): A FastAPI server that connects the dashboard to the chat interface.
5. **Streamlit Dashboard** (`dashboard.py`): An alternative dashboard using Streamlit.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd <repository-directory>
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

### Running the API Server

To start the API server:

```
python api_server.py
```

This will start the server on `http://localhost:8000`. You can access the dashboard at `http://localhost:8000/static/dashboard.html`.

### Running the Streamlit Dashboard

To start the Streamlit dashboard:

```
streamlit run dashboard.py
```

This will start the dashboard on `http://localhost:8501`.

### Using the Dashboard

1. Open the dashboard in your web browser.
2. Use the chat input to send commands to the assistant.
3. The assistant will respond with the results of your commands.
4. You can also use the quick actions in the sidebar to perform common tasks.

### Example Commands

- "Log in to Indeed"
- "Open the Network Engineer job"
- "Get applicants for the Test Engineer role"
- "Send an invite to all applicants for the Test Engineer role"
- "Update the status of John Doe to Interviewed"
- "Search for jobs matching Software Engineer"
- "Create a job post for Senior Developer"

## Development

### Adding New Commands

To add a new command to the chat interface:

1. Add a new function to `browser_tool/indeed_automation.py` for the automation task.
2. Add a new method to the `ChatInterface` class in `chat_interface.py` to handle the command.
3. Update the command processing logic in the `process_command` method of the `ChatInterface` class.

### Customizing the Dashboard

The dashboard can be customized by modifying the HTML and CSS in `dashboard.html`. The JavaScript code handles the interaction with the API server.

## Troubleshooting

### Common Issues

- **Connection Issues**: If you're having trouble connecting to the API server, make sure it's running and accessible from your browser.
- **Command Not Recognized**: If a command is not recognized, check the format of the command and make sure it matches one of the supported patterns.
- **Browser Automation Issues**: If the browser automation is not working correctly, check the logs for error messages and make sure the Indeed website is accessible.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

