import requests
import json


def login(sid: str, csrf: str, username: str, password: str) -> int:
    # print("Setting URL")
    url = "https://vle.mathswatch.co.uk/duocms/api/login"
    # print(f"URL set to: {url}")

    # print("Creating payload")
    payload = json.dumps({"username": username, "password": password})
    # print(f"Payload created: {payload}")

    # print("Setting headers")
    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://vle.mathswatch.co.uk",
        "priority": "u=1, i",
        "referer": "https://vle.mathswatch.co.uk/vle/",
        "cookie": f"connect.sid={sid}",
        "x-csrf-token": csrf,
    }
    # print(f"Headers set: {headers}")

    # print("Sending POST request")
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.status_code
    except requests.RequestException as e:
        print(f"Error during login request: {e}")
        return None
