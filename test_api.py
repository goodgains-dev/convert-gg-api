import requests
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
API_URL = "http://localhost:8000"  # Change this to your deployed API URL if testing remotely
API_KEY = os.getenv("API_KEY")

# Headers for API requests
headers = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}

def test_list_configs():
    """Test the /configs endpoint"""
    response = requests.get(f"{API_URL}/configs", headers=headers)
    
    if response.status_code == 200:
        print("✅ Successfully retrieved configurations")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Failed to retrieve configurations: {response.status_code}")
        print(response.text)

def test_crawl_with_config():
    """Test the /crawl endpoint with a predefined configuration"""
    payload = {
        "config_name": "test"  # Use the test configuration
    }
    
    response = requests.post(f"{API_URL}/crawl", headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ Successfully crawled with predefined configuration")
        result = response.json()
        print(f"Total items: {result['stats']['total_items']}")
        print(f"Pages crawled: {result['stats']['pages_crawled']}")
        print("First item:")
        print(json.dumps(result['items'][0] if result['items'] else {}, indent=2))
    else:
        print(f"❌ Failed to crawl: {response.status_code}")
        print(response.text)

def test_crawl_with_custom_config():
    """Test the /crawl endpoint with a custom configuration"""
    # Example custom configuration for a simple test
    payload = {
        "custom_config": {
            "BASE_URL": "https://example.com",
            "CSS_SELECTOR": "div.container",
            "REQUIRED_KEYS": ["title", "description"],
            "OPTIONAL_KEYS": ["link"],
            "CRAWLER_CONFIG": {
                "MULTI_PAGE": False,
                "HEADLESS": True,
                "USER_AGENT": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                "TIMEOUT": 30000,
                "WAIT_FOR": 1000
            },
            "LLM_CONFIG": {
                "MODEL": "llama3-70b-8192",
                "TEMPERATURE": 0.2,
                "MAX_TOKENS": 1024,
                "INSTRUCTION": "Extract the title and description from the page. If available, also extract any links."
            }
        }
    }
    
    response = requests.post(f"{API_URL}/crawl", headers=headers, json=payload)
    
    if response.status_code == 200:
        print("✅ Successfully crawled with custom configuration")
        result = response.json()
        print(f"Total items: {result['stats']['total_items']}")
        print(f"Pages crawled: {result['stats']['pages_crawled']}")
        print("First item:")
        print(json.dumps(result['items'][0] if result['items'] else {}, indent=2))
    else:
        print(f"❌ Failed to crawl: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    print("Testing DeepSeek Web Crawler API...")
    print("-" * 50)
    
    # Test listing configurations
    print("\n1. Testing /configs endpoint:")
    test_list_configs()
    
    # Test crawling with predefined configuration
    print("\n2. Testing /crawl endpoint with predefined configuration:")
    test_crawl_with_config()
    
    # Test crawling with custom configuration
    print("\n3. Testing /crawl endpoint with custom configuration:")
    test_crawl_with_custom_config()
