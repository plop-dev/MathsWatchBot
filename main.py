from utils import (
    getcookies,
    login,
    extractanswers,
    logout,
    getrecent,
    getquiz,
    find_user_info,
    find_class,
)

import sys
import json
from sympy.parsing.latex import parse_latex
from sympy import pretty
from rich.console import Console
from rich.padding import Padding
from dotenv import load_dotenv
import os

load_dotenv(dotenv_path=".env")

USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("PASSWORD")
INFO = os.getenv("INFO")
SUCCESS = os.getenv("SUCCESS")
DANGER = os.getenv("DANGER")

console = Console()

cookies = {}


def getanswer(username: str, quiz_id) -> None:
    global cookies
    console.print("[*] Getting cookies...", style=INFO)
    cookies = getcookies(username, PASSWORD)

    console.print("[*] Logging in...", style=INFO)
    login_info = login(cookies["connect.sid"], cookies["_csrf"], USERNAME, PASSWORD)
    console.print(f"[+] Login status: {login_info}", style=SUCCESS)

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


def main(quiz_id: int | None = None) -> None:
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
    console.print(f"[+] Login status: {login_info}", style=SUCCESS)
    if login_info != 200:
        console.print(
            f"[!] Error {login_info}: Could not get user data.\n[i]Exiting...[/i]",
            style=DANGER,
        )
        sys.exit()

    console.print("[+] Successfully logged into default user account.", style=SUCCESS)

    if quiz_id is None:
        console.print("[*] Getting recent quiz ID...", style=INFO)
        recent_quiz_id = getrecent(def_cookies["connect.sid"], def_cookies["_csrf"])
        console.print(
            f"[+] Recent quiz ID: {recent_quiz_id['id']} ({recent_quiz_id['name']})",
            style=SUCCESS,
        )
    else:
        console.print("[*] Using provided quiz ID...", style=INFO)
        recent_quiz_id = getquiz(
            def_cookies["connect.sid"], def_cookies["_csrf"], quiz_id
        )
        console.print(
            f"[+] Recent quiz ID: {recent_quiz_id['id']} ({recent_quiz_id['name']})",
            style=SUCCESS,
        )

    console.print("[*] Logging out...", style=INFO)
    logout(def_cookies["connect.sid"], def_cookies["_csrf"])
    console.print("[+] Logged out", style=SUCCESS)
    console.rule()

    del def_cookies

    # loop through all users in the class
    with open("users.json", "r") as file:
        answers_found = 0
        total_users = 0
        users = json.load(file)[user_class]

        for user in users:
            total_users += 1
            console.print(f"[*] Getting answers for {user['username']}...", style=INFO)
            res = getanswer(user["username"], recent_quiz_id)

            if res == "skipped":
                continue
            else:
                answers_found += 1
                console.print(
                    f"[+] Answers for {user['username']} ({user['first_name'] + ' ' + user['surname']}) retrieved",
                    style=SUCCESS,
                )
                break

    console.print(
        f"[{SUCCESS}]Results:[/]",
        Padding(
            f"Users Searched: {total_users}\nAnswers found: {answers_found}\nAnswers skipped: {total_users - answers_found}",
            (0, 2),
        ),
    )


if __name__ == "__main__":
    main(9442834)
