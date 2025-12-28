import requests
import json

def test_instahyre():
    url = "https://www.instahyre.com/api/v1/job_search"
    params = {
        "skills": "Data Engineer",
        "location": "Pune",
        "count": 10
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.instahyre.com/jobs/"
    }
    
    print("Testing Instahyre API...")
    try:
        resp = requests.get(url, params=params, headers=headers)
        print(f"Status Code: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            # print(json.dumps(data, indent=2)) 
            # Commented out to avoid clutter, just checking structure
            if 'objects' in data:
                print(f"Found {len(data['objects'])} jobs.")
                for obj in data['objects'][:3]:
                    print(f"- {obj.get('title')} @ {obj.get('company_name')}")
            else:
                print("No 'objects' key in response.")
        else:
            print("Failed to access API.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_instahyre()
