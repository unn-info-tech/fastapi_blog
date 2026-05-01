import requests
import time

url = "http://localhost:8000/login"

data = {
    "username": "user@example12.com",
    "password": "string"
}

for i in range(1, 7):  # 6 attempts
    response = requests.post(url, data=data)

    print(f"Attempt {i}")
    print("Status:", response.status_code)

    try:
        print("Response:", response.json())
    except:
        print("Response text:", response.text)

    print("-" * 30)

    time.sleep(1)  # small delay (optional)