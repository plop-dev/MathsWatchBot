import requests
import json


def getcookies(username: str, password: str) -> dict:
    url = "https://vle.mathswatch.co.uk/vle/"
    # print(f"URL: {url}")

    payload = json.dumps({"username": username, "password": password})
    # print(f"Payload: {payload}")

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://vle.mathswatch.co.uk",
        "priority": "u=1, i",
        "referer": "https://vle.mathswatch.co.uk/vle/",
    }
    # print(f"Headers: {headers}")

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        # print(f"Response Status Code: {response.status_code}")
        # print(f"Response Cookies: {response.cookies}")

        cookies = response.cookies.get_dict()
        # print(f"Cookies: {cookies}")

        return cookies
    except requests.RequestException as e:
        print(f"Error during getcookies request: {e}")
        return None
