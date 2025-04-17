import asyncio
import logging
from browser_tool.indeed_automation import login_to_indeed

# Set up logging to see detailed output
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    print("Starting Indeed login test...")
    try:
        result = await login_to_indeed()
        print(f"Login result: {result}")
    except Exception as e:
        print(f"Error during login: {e}")
    print("Test completed.")

if __name__ == "__main__":
    asyncio.run(main()) 