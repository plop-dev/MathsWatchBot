import re
from utils import (
    get_working_out,
    getcookies,
    login,
    extractanswers,
    logout,
    getrecent,
    getquiz,
    find_user_info,
    find_class,
    convert_latex_to_unicode,
    downloadquestion,
    crop_whitespace,
    run_once,
)

import sys
import json
from rich.console import Console
from rich.padding import Padding
from rich.panel import Panel
from rich.markdown import Markdown
from dotenv import load_dotenv
import os

load_dotenv()

USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("PASSWORD")
INFO = os.getenv("INFO")
SUCCESS = os.getenv("SUCCESS")
DANGER = os.getenv("DANGER")

console = Console()

cookies = {}
total_questions = 0


def processanswerfunc(question_id: int) -> None:
    console.print("[*] Downloading question...", style=INFO)
    download_status = downloadquestion(question_id)
    if download_status != 200:
        if download_status == 10000:
            console.print(f"[*] Question already {question_id} downloaded.", style=INFO)
        else:
            console.print(
                f"[!] Error {download_status}: Could not download question {question_id}.",
                style=DANGER,
            )
    else:
        console.print(f"[+] Question {question_id} downloaded.", style=SUCCESS)

    console.print("[*] Cropping whitespace...", style=INFO)
    crop_status = crop_whitespace(
        f"./questions/{question_id}.png",
        f"./questions/{question_id}.png",
    )
    if crop_status != 200:
        if crop_status == 10000:
            console.print(
                f"[*] Whitespace already for question {question_id}.", style=INFO
            )
        else:
            console.print(
                f"[!] Error {crop_status}: Could not crop whitespace for question {question_id}.",
                style=DANGER,
            )
    else:
        console.print(
            f"[+] Whitespace cropped for question {question_id}.", style=SUCCESS
        )


processanswer = run_once(processanswerfunc)


def getanswer(username: dict, quiz_id: dict, working_out: bool = False) -> dict:
    global cookies
    console.print("[*] Getting cookies...", style=INFO)
    cookies = getcookies(username["username"], PASSWORD)

    console.print("[*] Logging in...", style=INFO)
    login_info = login(
        cookies["connect.sid"], cookies["_csrf"], username["username"], PASSWORD
    )
    console.print(f"[+] Login status: {login_info}", style=SUCCESS)

    if login_info != 200:
        console.print(
            f"[!] Error {login_info}: Could not get user data.\n[i]Skipping user[/i]",
            style=DANGER,
        )
        return None

    console.print("[*] Getting answers...", style=INFO)
    answers = extractanswers(cookies["connect.sid"], cookies["_csrf"], quiz_id["id"])
    if answers is None:
        console.print("[!] Error: Could not get answers.", style=DANGER)
        return None
    console.print(f"[+] Answers: {len(answers['answers'])}", style=SUCCESS)

    user_info = username

    if len(answers["answers"]) == 0:
        console.print("[*] Logging out...", style=INFO)
        logout(cookies["connect.sid"], cookies["_csrf"])
        console.print("[+] Logged out", style=SUCCESS)

        console.print(
            f"[!] No answers found for {username['username']} ({user_info['first_name'].strip() + ' ' + user_info['surname']})\n[i]Skipping user...[/]",
            style=DANGER,
        )
        console.rule()
        return "skipped"

    extracted_answers = {}
    question_ids = {}

    for i in range(len(answers["answers"])):
        for j in range(len(answers["answers"][i]["answer"])):
            answer = answers["answers"][i]["answer"][j]["text"]
            question_id = answers["answers"][i]["question_id"]

            if (
                working_out
                and not processanswer.has_run
                and (total_questions == len(answers["answers"]))
            ):
                processanswer(question_id)
                processanswer.has_run = False

            if isinstance(answer, list):
                answer = str(answer)  # Convert list to string for hashing
            if f"{i + 1}" not in extracted_answers:
                extracted_answers[f"{i + 1}"] = {}
            if f"{j + 1}" not in extracted_answers[f"{i + 1}"]:
                extracted_answers[f"{i + 1}"][f"{j + 1}"] = {}
            if answer not in extracted_answers[f"{i + 1}"][f"{j + 1}"]:
                extracted_answers[f"{i + 1}"][f"{j + 1}"][answer] = 0
            extracted_answers[f"{i + 1}"][f"{j + 1}"][answer] += 1

            # Store the question_id separately
            question_ids[f"{i + 1}"] = question_id

    console.print("[*] Logging out...", style=INFO)
    logout(cookies["connect.sid"], cookies["_csrf"])
    console.print("[+] Logged out", style=SUCCESS)

    if (
        working_out
        and not processanswer.has_run
        and (total_questions == len(answers["answers"]))
    ):
        processanswer.has_run = True
    # sys.exit(-1)
    return extracted_answers, question_ids


def main(quiz_id: int | None = None, use_working_out: bool | None = None) -> None:
    global total_questions

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
        quiz_info = getquiz(
            def_cookies["connect.sid"], def_cookies["_csrf"], recent_quiz_id["id"]
        )
        total_questions = quiz_info["num_questions"]

        console.print(
            f"[+] Recent quiz ID: {recent_quiz_id['id']} ({recent_quiz_id['name']})",
            style=SUCCESS,
        )
    else:
        console.print("[*] Using provided quiz ID...", style=INFO)
        recent_quiz_id = getquiz(
            def_cookies["connect.sid"], def_cookies["_csrf"], quiz_id
        )
        total_questions = recent_quiz_id["num_questions"]
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
        all_question_ids = {}

        for user in users:
            total_users += 1
            console.rule(
                f"[{INFO}]User: {user['username']} ({user['first_name'].strip() + ' ' + user['surname']})[/]",
                align="left",
            )
            res = getanswer(user, recent_quiz_id, use_working_out)

            if res == "skipped":
                continue
            elif res is None:
                continue
            else:
                answers_found += 1
                extracted_answers, question_ids = res

                for question, answers in extracted_answers.items():
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

                # Store the question_ids
                for question, question_id in question_ids.items():
                    all_question_ids[question] = question_id

        most_common_answers = {}
        for question, answers in all_extracted_answers.items():
            most_common_answers[question] = {}
            for sub_question, sub_answers in answers.items():
                most_common_answer = max(sub_answers, key=sub_answers.get)
                most_common_answers[question][sub_question] = most_common_answer

        working_out = {}

        if use_working_out:
            for file in os.listdir("./questions"):
                working_out_file = "working_out.json"

                # if os.path.exists(working_out_file) and processanswer.has_run:
                if os.path.exists(working_out_file):
                    with open(working_out_file, "r") as f:
                        working_out = json.load(f)
                else:
                    working_out = {}

                for file in os.listdir("./questions"):
                    question_id = file.split(".")[0]
                    if file.endswith(".png") and question_id not in working_out:
                        console.print(
                            f"[*] Generating working out for {file}...", style=INFO
                        )
                        answer = get_working_out(f"./questions/{file}")
                        console.print(
                            f"[+] Working out generated for {file}.", style=SUCCESS
                        )

                        latex = convert_latex_to_unicode(answer)
                        latex = re.sub(
                            r"(\*\*)ANSWER(\s[a-g]|)?(\*\*)", r"ANSWER\2", latex
                        )

                        print(latex)

                        sub_working_outs = re.split(r"(ANSWER)((\s[a-g])|)", latex)
                        sub_working_outs = [
                            s.strip() for s in sub_working_outs if s and s.strip()
                        ]

                        working_out[question_id] = sub_working_outs

                # Save the working out to a file
                with open(working_out_file, "w") as f:
                    json.dump(working_out, f)

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
                    question_id = all_question_ids[f"{i + 1}"]

                    try:
                        expr = answer.replace("[", "").replace("]", "").replace("'", "")
                    except Exception as e:
                        console.print(
                            f"Error parsing answer: {answer}: {e}", style=DANGER
                        )
                        continue

                    if use_working_out:
                        console.print(
                            Padding(
                                f"[{SUCCESS}]Answer {j + 1} (id: {question_id})[/]:",
                                (0, 2),
                            )
                        )
                        console.print(
                            Padding(
                                Panel(
                                    Markdown(f"{working_out[str(question_id)][j]}"),
                                    title="Working Out",
                                    title_align="left",
                                ),
                                (0, 4),
                            ),
                        )

                    console.print(
                        Padding(
                            Panel(
                                f"{convert_latex_to_unicode(expr)}",
                                title="Answer",
                                title_align="left",
                            ),
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
    # main(9442834, True)
    main(use_working_out=True)
    # 9442834
