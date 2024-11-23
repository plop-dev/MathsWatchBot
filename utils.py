import requests
import sys
import json
from rich.console import Console
from bisect import bisect_left
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("USERNAME")
PASSWORD = os.getenv("PASSWORD")
INFO = os.getenv("INFO")
SUCCESS = os.getenv("SUCCESS")
DANGER = os.getenv("DANGER")

console = Console()


def generate_headers(sid: str | None = None, csrf: str | None = None) -> dict:
    if sid is None or csrf is None:
        return {
            "accept": "*/*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
            "content-type": "application/json",
            "dnt": "1",
            "origin": "https://vle.mathswatch.co.uk",
            "priority": "u=1, i",
            "referer": "https://vle.mathswatch.co.uk/vle/",
        }
    else:
        return {
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


def extractanswers(sid: str, csrf: str, qid: str) -> dict:
    url = f"https://vle.mathswatch.co.uk/duocms/api/answers?assignedwork_id={qid}"
    payload = {}
    headers = generate_headers(sid, csrf)
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


def getcookies(username: str, password: str) -> dict:
    url = "https://vle.mathswatch.co.uk/vle/"
    payload = json.dumps({"username": username, "password": password})
    headers = generate_headers()

    try:
        response = requests.request("GET", url, headers=headers, data=payload)
        cookies = response.cookies.get_dict()
        return cookies
    except requests.RequestException as e:
        print(f"Error during getcookies request: {e}")
        return None


def getrecent(sid: str, csrf: str) -> dict:
    url = "https://vle.mathswatch.co.uk/duocms/api/assignedwork/student"
    params = {"recent": "true"}
    headers = generate_headers(sid, csrf)

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


def login(sid: str, csrf: str, username: str, password: str) -> int:
    url = "https://vle.mathswatch.co.uk/duocms/api/login"
    payload = json.dumps({"username": username, "password": password})
    headers = generate_headers(sid, csrf)

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.status_code
    except requests.RequestException as e:
        print(f"Error during login request: {e}")
        return None


def logout(sid: str, csrf: str) -> int:
    url = "https://vle.mathswatch.co.uk/duocms/api/logout"
    payload = {}
    headers = generate_headers(sid, csrf)

    try:
        request = requests.request("GET", url, headers=headers, data=payload)
        return request.status_code
    except requests.RequestException as e:
        print(f"Error during logout request: {e}")
        return None


def find_user_info(username: str) -> dict:
    try:
        with open("users.json", "r") as file:
            classes = json.load(file)
    except Exception as e:
        console.print(
            f"[!] Unable to open users.json. Reason: {e}\nHave you run recon.py?",
            style=DANGER,
        )
        sys.exit()

    for class_name, users in classes.items():
        index = bisect_left([user["username"] for user in users], username)
        if index != len(users) and users[index]["username"] == username:
            return users[index]

    return None


def find_class(username: str) -> str:
    try:
        with open("users.json", "r") as file:
            classes = json.load(file)
    except Exception as e:
        console.print(
            f"[!] Unable to open users.json. Reason: {e}\nHave you run recon.py?",
            style=DANGER,
        )
        sys.exit()

    for class_name, users in classes.items():
        index = bisect_left([user["username"] for user in users], username)
        if index != len(users) and users[index]["username"] == username:
            return class_name

    return None
