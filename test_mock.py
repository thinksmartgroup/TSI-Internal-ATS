import asyncio
import json
from browser_tool.agent import use_browser

async def test_mock_dashboard():
    """Test the browser tool with a mock Indeed dashboard task"""
    print("Testing browser tool with mock Indeed dashboard...")
    
    try:
        # Define the task with mock data
        task = """
        Create a mock Indeed employer dashboard with sample application data.
        Return the data in JSON format with fields: name, position, date, status, experience, skills.
        
        Include at least 5 sample applications with realistic data.
        """
        
        # Run the browser tool
        result = await use_browser(task)
        
        # Try to parse the result as JSON
        try:
            applications = json.loads(result)
            print(f"Successfully created {len(applications)} mock applications")
            
            # Print all applications
            print("\nMock applications:")
            print(json.dumps(applications, indent=2))
                
        except json.JSONDecodeError:
            print("Error: Result is not valid JSON")
            print("Raw result:", result)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_mock_dashboard()) 