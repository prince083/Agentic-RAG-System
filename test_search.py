import requests
import time

def test_search():
    url = "http://localhost:8000/api/v1/search"
    query = {"query": "test pipeline", "k": 3}
    
    print("Searching...")
    try:
        response = requests.post(url, json=query)
        if response.status_code == 200:
            print("Search Results:")
            results = response.json()
            for i, res in enumerate(results):
                print(f"{i+1}. {res['text'][:100]}... (Score: {res['score']})")
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
