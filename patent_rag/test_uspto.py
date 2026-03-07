import os
import json
import logging
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_uspto():
    query = "LiDAR based navigation for drones"
    # USPTO PFW Search API endpoint
    url = "https://api.uspto.gov/api/v1/patent/applications/search"
    api_key = os.getenv("USPTO_API_KEY")
    
    headers = {"X-Api-Key": api_key} if api_key else {}
    # Simplified syntax: applicationMetaData.inventionTitle:query OR applicationMetaData.abstractText:query
    params = {
        "q": f"applicationMetaData.inventionTitle:{query} OR applicationMetaData.abstractText:{query}",
        "limit": 2
    }
    
    print(f"URL: {url}")
    print(f"Headers: {'(Key Present)' if api_key else '(No Key)'}")
    print(f"Params: {params}")
    
    try:
        response = requests.get(url, params=params, headers=headers)
        if response.status_code == 401:
            print("Error: 401 Unauthorized. Please check your USPTO_API_KEY in .env")
            return
            
        response.raise_for_status()
        data = response.json()
        print(f"Status: {response.status_code}")
        
        results = data.get("results", [])
        print(f"Results Count: {len(results)}")
        if results:
            for item in results:
                meta = item.get("applicationMetaData", {})
                app_num = meta.get("applicationNumberText")
                title = meta.get("inventionTitle")
                print(f"Patent/Application: {app_num} - {title}")
        else:
            print("No results found.")
            print(f"Full Response: {json.dumps(data, indent=2)}")
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_uspto()
