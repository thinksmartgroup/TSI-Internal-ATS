import asyncio
import json
from browser_tool.agent import use_browser

async def test_indeed_dashboard():
    """Test the browser tool with the Indeed employer dashboard task"""
    print("Testing browser tool with Indeed employer dashboard...")
    
    try:
        # Define the task
        task = "Check the Indeed employer dashboard for new applications and return them in JSON format with fields: name, position, date, status, experience, skills"
        
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
    asyncio.run(test_indeed_dashboard()) 