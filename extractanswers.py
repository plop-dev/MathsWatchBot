import requests
import json


def extractanswers(sid: str, csrf: str, qid: str) -> dict:
    # print("Constructing URL")
    url = f"https://vle.mathswatch.co.uk/duocms/api/answers?assignedwork_id={qid}"
    # print(f"URL constructed: {url}")

    payload = {}
    # print("Payload initialized")

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
    # print("Headers initialized")

    # print("Sending GET request")
    try:
        request = requests.request("GET", url, headers=headers, data=payload)
        response = json.loads(request.text.replace("'", '"'))
        answers = {
            "status": response["status"],
            "answers": response["data"],
        }
        return answers
    except requests.RequestException as e:
        print(f"Error during extractanswers request: {e}")
        return None
    except (json.JSONDecodeError, KeyError) as e:
        print(f"Error parsing extractanswers response: {e}")
        return None
