
import requests
import io
import json

def test_upload():
    url = "http://localhost:8000/api/"
    
    # Create rudimentary CSV data
    csv_content = """id,category,value
1,A,100
2,B,200
3,A,150
4,C,50
5,B,120"""
    
    files = {
        'questions.txt': ('questions.txt', 'Analyze this data', 'text/plain'),
        'data.csv': ('data.csv', csv_content, 'text/csv')
    }
    
    try:
        print(f"Sending request to {url}...")
        response = requests.post(url, files=files)
        
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print("Response JSON Summary:")
            print(f"Summary: {data.get('summary')}")
            print(f"Status: {data.get('status')}")
            print(f"Visualizations: {len(data.get('visualizations', []))} generated")
            print(f"Data Keys: {list(data.get('data', {}).keys())}")
        else:
            print("Response Text:")
            print(response.text)
            
    except Exception as e:
        print(f"Test Failed: {e}")

if __name__ == "__main__":
    test_upload()
