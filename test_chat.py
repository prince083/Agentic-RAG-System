import requests

def test_chat():
    url = "http://localhost:8000/api/v1/chat"
    
    # Question based on the test PDF we created
    question = "What is this document about?"
    
    print(f"Question: {question}")
    print("Asking Agent...")
    
    try:
        response = requests.post(url, json={"message": question})
        if response.status_code == 200:
            data = response.json()
            print("\n--- Answer ---")
            print(data["answer"])
            print("\n--- Sources ---")
            print(data["sources"])
        else:
            print(f"Failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_chat()
