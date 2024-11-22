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
    request = requests.request("GET", url, headers=headers, data=payload)
    response = json.loads(request.text.replace("'", '"'))
    # print("Response received")

    answers = {}
    # print("Extracting status from response")
    answers["status"] = response["status"]

    # print("Extracting answers from response")
    answers["answers"] = response["data"]
    # print("Answers extracted")

    return answers
