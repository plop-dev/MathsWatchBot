from getcookies import getcookies
from login import login
from extractanswers import extractanswers
from logout import logout
from getrecent import getrecent

import sys
import json
from sympy.parsing.latex import parse_latex
from sympy import pretty
from rich.console import Console
from rich.padding import Padding
from bisect import bisect_left

USERNAME = "5287@stgcc"
PASSWORD = "Triangle"

console = Console()
INFO = "bold blue"
SUCCESS = "bold green"
DANGER = "bold red"

cookies = {}


def find_user_info(username: str) -> dict:
    with open("users.json", "r") as file:
        classes = json.load(file)

    for class_name, users in classes.items():
        index = bisect_left([user["username"] for user in users], username)
        if index != len(users) and users[index]["username"] == username:
            return users[index]

    return None


def find_class(username: str) -> str:
    with open("users.json", "r") as file:
        classes = json.load(file)

    for class_name, users in classes.items():
        index = bisect_left([user["username"] for user in users], username)
        if index != len(users) and users[index]["username"] == username:
            return class_name

    return None


def getanswer(username: str, quiz_id) -> None:
    global cookies
    console.print("[*] Getting cookies...", style=INFO)
    cookies = getcookies(username, PASSWORD)

    console.print("[*] Logging in...", style=INFO)
    login_info = login(cookies["connect.sid"], cookies["_csrf"], USERNAME, PASSWORD)
    console.print(f"[+] Login info: {login_info}", style=SUCCESS)

    if login_info != 200:
        console.print(
            f"[!] Error {login_info}: Could not get user data.\n[i]Skipping user[/i]",
            style=DANGER,
        )
        return None

    console.print("[*] Getting answers...", style=INFO)
    answers = extractanswers(cookies["connect.sid"], cookies["_csrf"], quiz_id)
    console.print(f"[+] Answers: {len(answers['answers'])}", style=SUCCESS)

    if len(answers["answers"]) == 0:
        console.print("[*] Logging out...", style=INFO)
        logout(cookies["connect.sid"], cookies["_csrf"])
        console.print("[+] Logged out", style=SUCCESS)

        user_info = find_user_info(username)
        console.print(
            f"[!] No answers found for {username} ({user_info['first_name'] + ' ' + user_info['surname']})\n[i]Skipping user...[/]",
            style=DANGER,
        )
        console.rule()
        return "skipped"

    for i in range(len(answers["answers"])):
        console.print(Padding(f"[u][{INFO}]Question {i + 1}[/]:[/]\n", (0, 2)))

        for j in range(len(answers["answers"][i]["answer"])):
            answer = answers["answers"][i]["answer"][j]["text"]

            try:
                if type(answer) is list:
                    answer = answer[0]
                expr = parse_latex(answer)
            except Exception as e:
                console.print(f"Error parsing answer: {answer}: {e}", style=DANGER)
                continue

            console.print(
                Padding(
                    f"[u][{SUCCESS}]Answer {j + 1}[/]:[/]\n{pretty(expr, use_unicode=True)}\n",
                    (0, 2),
                )
            )

        if i + 1 != len(answers["answers"]):
            console.rule()

    console.print("[*] Logging out...", style=INFO)
    logout(cookies["connect.sid"], cookies["_csrf"])
    console.print("[+] Logged out", style=SUCCESS)
    return "success"


def main():
    console.print(
        f"[*] Starting the script with default user: {USERNAME} ({find_user_info(USERNAME)['first_name'] + ' ' + find_user_info(USERNAME)['surname']})...",
        style=INFO,
    )

    console.print("[*] Getting default user class...", style=INFO)
    user_class = find_class(USERNAME)
    console.print(f"[+] Default user class found: {user_class}", style=SUCCESS)

    console.print("[*] Getting cookies...", style=INFO)
    def_cookies = getcookies(USERNAME, PASSWORD)

    console.print("[*] Logging in...", style=INFO)
    login_info = login(
        def_cookies["connect.sid"], def_cookies["_csrf"], USERNAME, PASSWORD
    )
    console.print(f"[+] Login info: {login_info}", style=SUCCESS)
    if login_info != 200:
        console.print(
            f"[!] Error {login_info}: Could not get user data.\n[i]Exiting...[/i]",
            style=DANGER,
        )
        sys.exit()

    console.print("[+] Successfully logged into default user account.", style=SUCCESS)

    console.print("[*] Getting recent quiz ID...", style=INFO)
    recent_quiz_id = getrecent(def_cookies["connect.sid"], def_cookies["_csrf"])
    console.print(
        f"[+] Recent quiz ID: {recent_quiz_id['id']} ({recent_quiz_id['name']})",
        style=SUCCESS,
    )

    console.print("[*] Logging out...", style=INFO)
    logout(def_cookies["connect.sid"], def_cookies["_csrf"])
    console.print("[+] Logged out", style=SUCCESS)

    del def_cookies

    # loop through all users in the class
    with open("users.json", "r") as file:
        users = json.load(file)[user_class]

        for user in users:
            console.print(f"[*] Getting answers for {user['username']}...", style=INFO)
            res = getanswer(user["username"], recent_quiz_id)

            if res == "skipped":
                continue
            else:
                console.print(
                    f"[+] Answers for {user['username']} ({user['first_name'] + ' ' + user['surname']}) retrieved",
                    style=SUCCESS,
                )
                break


if __name__ == "__main__":
    main()
