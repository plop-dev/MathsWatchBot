import requests


def logout(sid: str, csrf: str) -> int:
    url = "https://vle.mathswatch.co.uk/duocms/api/logout"
    payload = {}

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

    request = requests.request("GET", url, headers=headers, data=payload)

    return request.status_code
