import asyncio
import json
from browser_tool.agent import use_browser

async def test_cloudflare_with_url():
    """Test the browser tool with Cloudflare verification handling on a specific URL"""
    print("Testing browser tool with Cloudflare verification handling...")
    
    try:
        # Define the task with a specific URL
        task = """
        Navigate to https://employers.indeed.com/.
        If you encounter a Cloudflare verification, wait for manual verification.
        After verification, extract any visible information and return it in JSON format.
        """
        
        # Run the browser tool
        result = await use_browser(task)
        
        # Try to parse the result as JSON
        try:
            data = json.loads(result)
            print("Successfully retrieved data after Cloudflare verification")
            print("\nData:")
            print(json.dumps(data, indent=2))
                
        except json.JSONDecodeError:
            print("Error: Result is not valid JSON")
            print("Raw result:", result)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_cloudflare_with_url()) 