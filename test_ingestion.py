import requests
import time
import os

def test_ingestion():
    url = "http://localhost:8000/api/v1/ingest"
    file_path = "test_doc.pdf"
    
    print("Waiting for server...")
    for _ in range(30):
        try:
            requests.get("http://localhost:8000/health")
            break
        except:
            time.sleep(1)
    else:
        print("Server did not start in time.")
        return

    print("Uploading PDF...")
    with open(file_path, "rb") as f:
        files = {"file": ("test_doc.pdf", f, "application/pdf")}
        response = requests.post(url, files=files)
    
    if response.status_code == 200:
        print("Success! Response:")
        print(response.json())
    else:
        print(f"Failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_ingestion()
