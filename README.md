# Think Smart Group Internal ATS


## Features

- **Real-time voice interaction** using WebSockets.
- **Integration with OpenAI's GPT-4** for natural language understanding.
- **Automated web browsing** via the `browser_use` tool.
- **Visual interface** to display the assistant's state.
- **Logging** of runtime and WebSocket events.

## Setup

### Prerequisites
- Ensure you have **Python 3.11 or later** (browser_use does not work with older versions).
- Install **Playwright** if any errors occur (`playwright install`).

### Installation Steps

**Create a virtual environment:**
   ```sh
   python3 -m venv venv
   ```
**Activate the virtual environment:**
   - **Linux/macOS:**
     ```sh
     source venv/bin/activate
     ```
   - **Windows:**
     ```sh
     venv\Scripts\activate
     ```
**Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
**Set up environment variables:**
   - Create a `.env` file based on `.env.sample`.
**Run the application:**
   ```sh
   python main.py
   ```

## Project Structure

```
voice-assistant/
├── assistant_modules/
│   ├── audio.py
│   ├── log_utils.py
│   ├── microphone.py
│   ├── utils.py
│   ├── visual_interface.py
│   └── websocket_handler.py
├── browser_tool/
│   └── agent.py
├── __pycache__/
├── .env
├── .env.sample
├── .gitignore
├── config.py
├── main.py
├── requirements.txt
├── runtime_time_table.jsonl
└── venv/
```

