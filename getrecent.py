import requests
import json


def getrecent(sid: str, csrf: str) -> dict:
    url = "https://vle.mathswatch.co.uk/duocms/api/assignedwork/student"
    # print(f"URL: {url}")

    params = {"recent": "true"}

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
    # print(f"Headers: {headers}")

    try:
        request = requests.request("GET", url, headers=headers, params=params)
        response = json.loads(request.text.replace("'", '"'))
        return {
            "id": response["data"][0]["id"],
            "name": response["data"][0]["title"],
        }
    except requests.RequestException as e:
        print(f"Error during getrecent request: {e}")
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        print(f"Error parsing getrecent response: {e}")
        return None
