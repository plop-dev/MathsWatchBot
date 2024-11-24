from utils import (
    getcookies,
    login,
    extractanswers,
    logout,
    getrecent,
    getquiz,
    find_user_info,
    find_class,
    convert_latex_to_unicode,
)

import sys
import json
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
    cookies = getcookies(username["username"], PASSWORD)

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

        user_info = username
        console.print(
            f"[!] No answers found for {username['username']} ({user_info['first_name'].strip() + ' ' + user_info['surname']})\n[i]Skipping user...[/]",
            style=DANGER,
        )
        console.rule()
        return "skipped"

    # for i in range(len(answers["answers"])):
    #     console.print(Padding(f"[u][{INFO}]Question {i + 1}[/]:[/]\n", (0, 2)))

    #     for j in range(len(answers["answers"][i]["answer"])):
    #         answer = answers["answers"][i]["answer"][j]["text"]

    #         try:
    #             if type(answer) is list:
    #                 answer = answer[0]
    #             expr = parse_latex(answer)
    #         except Exception as e:
    #             console.print(f"Error parsing answer: {answer}: {e}", style=DANGER)
    #             continue

    #         console.print(
    #             Padding(
    #                 f"[u][{SUCCESS}]Answer {j + 1}[/]:[/]\n{pretty(expr, use_unicode=True)}\n",
    #                 (0, 2),
    #             )
    #         )

    #     if i + 1 != len(answers["answers"]):
    #         console.rule()

    # console.print("[*] Logging out...", style=INFO)
    # logout(cookies["connect.sid"], cookies["_csrf"])
    # console.print("[+] Logged out", style=SUCCESS)
    # return "success"

    extracted_answers = {}

    for i in range(len(answers["answers"])):
        for j in range(len(answers["answers"][i]["answer"])):
            answer = answers["answers"][i]["answer"][j]["text"]
            if isinstance(answer, list):
                answer = str(answer)  # Convert list to string for hashing
            if f"{i + 1}" not in extracted_answers:
                extracted_answers[f"{i + 1}"] = {}
            if f"{j + 1}" not in extracted_answers[f"{i + 1}"]:
                extracted_answers[f"{i + 1}"][f"{j + 1}"] = {}
            if answer not in extracted_answers[f"{i + 1}"][f"{j + 1}"]:
                extracted_answers[f"{i + 1}"][f"{j + 1}"][answer] = 0
            extracted_answers[f"{i + 1}"][f"{j + 1}"][answer] += 1

    console.print("[*] Logging out...", style=INFO)
    logout(cookies["connect.sid"], cookies["_csrf"])
    console.print("[+] Logged out", style=SUCCESS)

    return extracted_answers


def main(quiz_id: int | None = None) -> None:
    console.print(
        f"[*] Starting the script with default user: {USERNAME} ({find_user_info(USERNAME)['first_name'].strip() + ' ' + find_user_info(USERNAME)['surname']})...",
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

    del def_cookies

    with open("users.json", "r") as file:
        answers_found = 0
        total_users = 0
        users = json.load(file)[user_class]

        all_extracted_answers = {}

        for user in users:
            total_users += 1
            console.rule(
                f"[{INFO}]User: {user['username']} ({user['first_name'].strip() + ' ' + user['surname']})[/]",
                align="left",
            )
            # console.print(
            #     f"[*] Getting answers for {user['username']} ({user['first_name'].strip() + ' ' + user['surname']})...",
            #     style=INFO,
            # )
            res = getanswer(user, recent_quiz_id)

            if res == "skipped":
                continue
            else:
                answers_found += 1
                console.print(
                    style=SUCCESS,
                )

                for question, answers in res.items():
                    if question not in all_extracted_answers:
                        all_extracted_answers[question] = {}
                    for sub_question, sub_answers in answers.items():
                        if sub_question not in all_extracted_answers[question]:
                            all_extracted_answers[question][sub_question] = {}
                        for answer, count in sub_answers.items():
                            if (
                                answer
                                not in all_extracted_answers[question][sub_question]
                            ):
                                all_extracted_answers[question][sub_question][
                                    answer
                                ] = 0
                            all_extracted_answers[question][sub_question][answer] += (
                                count
                            )

        # Determine the most common answers
        most_common_answers = {}
        for question, answers in all_extracted_answers.items():
            most_common_answers[question] = {}
            for sub_question, sub_answers in answers.items():
                most_common_answer = max(sub_answers, key=sub_answers.get)
                most_common_answers[question][sub_question] = most_common_answer

        if len(most_common_answers) == 0:
            console.print(
                f"[!] No answers found for any user in {user_class}.",
                style=DANGER,
            )
        else:
            console.rule(f"[{INFO}]Most Common Answers[/]", align="left")

            for i in range(len(most_common_answers)):
                console.print(f"\n[{INFO}]Question {i + 1}[/]:")

                for j in range(len(most_common_answers[f"{i + 1}"])):
                    answer = most_common_answers[f"{i + 1}"][f"{j + 1}"]

                    try:
                        expr = answer.replace("[", "").replace("]", "").replace("'", "")
                    except Exception as e:
                        console.print(
                            f"Error parsing answer: {answer}: {e}", style=DANGER
                        )
                        continue

                    console.print(Padding(f"[{SUCCESS}]Answer {j + 1}[/]:", (0, 2)))
                    console.print(
                        Padding(
                            f"{convert_latex_to_unicode(expr)}",
                            (0, 4),
                        )
                    )

    console.rule(f"[{SUCCESS}]Results:[/]", align="left")
    console.print(
        Padding(
            f"Users Searched: {total_users}\nAnswers found: {answers_found}\nAnswers skipped: {total_users - answers_found}",
            (0, 2),
        ),
    )


if __name__ == "__main__":
    main()
