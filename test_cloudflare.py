import asyncio
import json
from browser_tool.agent import use_browser

async def test_cloudflare_handling():
    """Test the browser tool with Cloudflare verification handling"""
    print("Testing browser tool with Cloudflare verification handling...")
    
    try:
        # Define the task
        task = """
        Navigate to the Indeed employer dashboard.
        If you encounter a Cloudflare verification, wait for manual verification.
        After verification, extract application information and return it in JSON format.
        """
        
        # Run the browser tool
        result = await use_browser(task)
        
        # Try to parse the result as JSON
        try:
            applications = json.loads(result)
            print(f"Successfully retrieved {len(applications)} applications")
            
            # Print the first application as an example
            if applications:
                print("\nExample application:")
                print(json.dumps(applications[0], indent=2))
            else:
                print("No applications found")
                
        except json.JSONDecodeError:
            print("Error: Result is not valid JSON")
            print("Raw result:", result)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_cloudflare_handling()) 