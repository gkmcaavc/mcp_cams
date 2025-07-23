import httpx
import json

# URL to send the request to
url = "http://localhost:8000/verify_serialnumber"

# JSON payload to send
payload = {
    "serial": "AIPL22806101",
    "auth_token": "COJJ7eiiPBGUfmIQPvh2PJWWDLX7OuKs"
}

# Headers for the request
headers = {
    "User-Agent": "SampleClient/1.0",
    "Accept": "application/json",
    "Content-Type": "application/json"
}

def send_post_request():
    try:
        response = httpx.post(url, json=payload, headers=headers, timeout=10.0)
        response.raise_for_status()
        print("Response received:")
        print(json.dumps(response.json(), indent=2))
    except httpx.RequestError as e:
        print(f"Request error: {e}")
    except httpx.HTTPStatusError as e:
        print(f"HTTP error: {e.response.status_code} - {e.response.text}")
    except Exception as e:
        print(f"Other error: {e}")

if __name__ == "__main__":
    send_post_request()
