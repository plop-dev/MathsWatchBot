import requests
import re
import sys
import json
import cv2
import numpy as np
from rich.console import Console
from bisect import bisect_left
from dotenv import load_dotenv
from openai import OpenAI
import base64
import os

load_dotenv()

USERNAME = os.getenv("LOGIN_USERNAME")
PASSWORD = os.getenv("PASSWORD")
INFO = os.getenv("INFO")
SUCCESS = os.getenv("SUCCESS")
DANGER = os.getenv("DANGER")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

console = Console()

try:
    client = OpenAI(api_key=OPENAI_API_KEY)
except Exception as e:
    console.print(
        f"[-] An error occured initialising OPENAI client. Reason: {e}",
        style=DANGER,
    )


def run_once(f):
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return f(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


def get_working_out(image_path):
    base64_image = encode_image(image_path)

    response = client.chat.completions.create(
        model="gpt-4o",
        temperature=0.05,
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "You provide the question, working out and answer(s). Display the workings and questions and answers in latex format. You might receive 1 or 2 questions that might be labelled; answer both and label them if necessary. Don't include \\begin or \\align or \\\\ or boxed in the latex. Separate each step with a new line (do not include equal signs, they will be a new line). Only have a very short and brief explanation for some steps only if necessary. Format the working out in a layout that is easy to read. Answer the question:",
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}",
                            "detail": "low",
                        },
                    },
                ],
            },
        ],
    )

    answer = response.choices[0].message.content.strip()

    return answer


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
    url = "https://vle.mathswatch.co.uk/duocms/api/answers"
    params = {"assignedwork_id": qid}
    headers = generate_headers(sid, csrf)

    try:
        request = requests.request("GET", url, headers=headers, params=params)
        response = json.loads(request.text.replace("'", '"'))
        answers = {
            "status": response["status"],
            "answers": response["data"],
        }
        return answers
    except requests.RequestException as e:
        console.print(f"[!] Error during extractanswers request: {e}", style=DANGER)
        return None
    except (json.JSONDecodeError, KeyError) as e:
        console.print(f"[!] Error parsing extractanswers response: {e}", style=DANGER)
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
        console.print(f"[!] Error during getcookies request: {e}", style=DANGER)
        return None


def getmarks(sid: str, csrf: str, qid: str) -> dict:
    url = "https://vle.mathswatch.co.uk/duocms/api/assignedwork/student"
    params = {"recent": "true"}
    headers = generate_headers(sid, csrf)

    try:
        request = requests.request("GET", url, headers=headers, params=params)
        response = json.loads(request.text.replace("'", '"'))

        quiz = next((quiz for quiz in response["data"] if quiz["id"] == qid), None)
        if quiz is None:
            raise KeyError(f"Quiz with id {qid} not found.")

        return {
            "total_marks": quiz["marks"],
            "student_marks": quiz["student_marks"],
        }
    except requests.RequestException as e:
        console.print(f"[!] Error during getmarks request: {e}", style=DANGER)
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        console.print(f"[!] Error parsing getmarks response: {e}", style=DANGER)
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
        console.print(f"[!] Error during getrecent request: {e}", style=DANGER)
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        console.print(f"[!] Error parsing getrecent response: {e}", style=DANGER)
        return None


def getquiz(sid: str, csrf: str, qid: str) -> dict:
    url = f"https://vle.mathswatch.co.uk/duocms/api/assignedwork/{qid}"
    params = {"id": qid}
    headers = generate_headers(sid, csrf)

    try:
        request = requests.request("GET", url, headers=headers, params=params)
        response = json.loads(request.text.replace("'", '"'))
        num_questions = len(response["data"]["questions"])
        return {
            "id": response["data"]["id"],
            "name": response["data"]["title"],
            "num_questions": num_questions,
        }
    except requests.RequestException as e:
        console.print(f"[!] Error during getrecent request: {e}", style=DANGER)
        return None
    except (json.JSONDecodeError, KeyError, IndexError) as e:
        console.print(f"[!] Error parsing getrecent response: {e}", style=DANGER)
        return None


def login(sid: str, csrf: str, username: str, password: str) -> tuple[int, str]:
    url = "https://vle.mathswatch.co.uk/duocms/api/login"
    payload = json.dumps({"username": username, "password": password})
    headers = generate_headers(sid, csrf)

    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        return response.status_code, response.reason
    except requests.RequestException as e:
        console.print(f"[!] Error during login request: {e}", style=DANGER)
        return None


def logout(sid: str, csrf: str) -> int:
    url = "https://vle.mathswatch.co.uk/duocms/api/logout"
    payload = {}
    headers = generate_headers(sid, csrf)

    try:
        request = requests.request("GET", url, headers=headers, data=payload)
        return request.status_code
    except requests.RequestException as e:
        console.print(f"[!] Error during logout request: {e}", style=DANGER)
        return None


def change_password(sid: str, csrf: str, username: dict, password: str) -> int:
    url = "https://vle.mathswatch.co.uk/duocms/api/users/me"
    payload = json.dumps(
        {
            "id": "me",
            "email": f"21{username['surname'].strip()[:3].lower()}{username['first_name'].strip()[:3].lower()}@stgcc.co.uk",
            "password": password,
            "anonymous": False,
        }
    )
    headers = generate_headers(sid, csrf)
    console.print_json(payload)

    try:
        request = requests.request("PUT", url, headers=headers, data=payload)
        return request.status_code, request.reason
    except requests.RequestException as e:
        console.print(f"[!] Error during change_password request: {e}", style=DANGER)
        return None


def find_user_info(username: str) -> dict:
    try:
        with open(f"{BASE_DIR}/users.json", "r") as file:
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

    console.print(f"[!] User ({username}) not found in users.json", style=DANGER)
    sys.exit()
    return None


def find_class(username: str) -> str:
    try:
        with open(f"{BASE_DIR}/users.json", "r") as file:
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

    console.print(f"[!] User ({username}) class not found in users.json", style=DANGER)
    sys.exit()
    return None


def downloadquestion(id: int) -> int:
    url = f"https://vle.mathswatch.co.uk/images/questions/question{id}.png"
    headers = generate_headers()
    file_path = f"./questions/{id}.png"

    if os.path.exists(file_path):
        console.print(f"[*] File {file_path} already exists.", style=SUCCESS)
        return 10000  # HTTP status code for OK

    try:
        request = requests.request("GET", url, headers=headers)
        with open(file_path, "wb") as file:
            file.write(request.content)

        return request.status_code
    except requests.RequestException as e:
        console.print(f"[!] Error during download question request: {e}", style=DANGER)
        return None


def convert_latex_to_unicode(latex_str):
    # Remove \left and \right
    latex_str = latex_str.replace(r"\left", "").replace(r"\right", "")

    # Replace common symbols
    symbol_replacements = {
        "\\pi": "π",
        "\\phi": "φ",
        "\\pm": "±",
        "\\times": "×",
        "\\e": "e",
        "&": "",
        "$": "",
        "\\cdot": "×",
        "\\(": "",
        "\\)": "",
        "minus": "-",
        "plus": "+",
        "times": "×",
    }
    for latex_cmd, unicode_char in symbol_replacements.items():
        latex_str = latex_str.replace(latex_cmd, unicode_char)

    # Function to convert superscripts
    def convert_superscripts(match):
        superscripts_map = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")
        content = match.group(1).strip("{}")
        return content.translate(superscripts_map)

    # Function to convert subscripts
    def convert_subscripts(match):
        subscripts_map = str.maketrans("0123456789+-=()n", "₀₁₂₃₄₅₆₇₈₉₊₋₌₍₎ₙ")
        content = match.group(1).strip("{}")
        return content.translate(subscripts_map)

    # Function to convert fractions with a dividing line
    def convert_fraction(match: re.Match[str]):
        numerator = match.group(1).strip()
        denominator = match.group(2).strip()
        length = max(len(numerator), len(denominator))
        line = "─" * length
        numerator = numerator.center(length)
        denominator = denominator.center(length)

        # if the fraction has an equal sign, place it in the middle of the line
        if "=" in match.group(0):
            line = "═ " + line[length:]
            denominator = denominator.center(length)
        return f"\n{numerator}\n{line}\n{denominator}\n"

    # Function to convert roots
    def convert_roots(match):
        index = match.group(1)
        radicand = match.group(2)
        if not index:
            return f"√({radicand})"
        else:
            superscripts_map = str.maketrans("0123456789+-=()n", "⁰¹²³⁴⁵⁶⁷⁸⁹⁺⁻⁼⁽⁾ⁿ")
            index_sup = index.translate(superscripts_map)
            return f"{index_sup}√({radicand})"

    # Apply all transformations
    transformed_str = latex_str
    # Convert fractions written with \frac{}
    transformed_str = re.sub(
        r"\\frac\{([^}]*)\}\{([^}]*)\}", convert_fraction, transformed_str
    )
    # Convert fractions written with '/'
    transformed_str = re.sub(
        r"(?<!\S)(.+?)\s*\/\s*(.+)",
        convert_fraction,
        transformed_str,
    )
    # Convert roots
    transformed_str = re.sub(
        r"\\sqrt(?:\[(.*?)\])?\{(.*?)\}", convert_roots, transformed_str
    )
    # Convert superscripts
    transformed_str = re.sub(r"\^(\{[^}]*\}|.)", convert_superscripts, transformed_str)
    # Convert subscripts
    transformed_str = re.sub(r"_(\{[^}]*\}|.)", convert_subscripts, transformed_str)

    # Handle new line characters
    transformed_str = transformed_str.replace("\\n", "\n")

    return transformed_str


QUESTIONS_DIR = os.path.join(BASE_DIR, "questions")

if not os.path.exists(QUESTIONS_DIR):
    os.makedirs(QUESTIONS_DIR)


def crop_whitespace(
    image_path: str = None,
    output_path: str = None,
) -> int:
    # Use the reusable QUESTIONS_DIR variable
    if image_path is None:
        image_path = os.path.join(QUESTIONS_DIR, "image.png")
    if output_path is None:
        output_path = os.path.join(QUESTIONS_DIR, "image_cropped.png")

    # Check if the output file already exists
    if os.path.exists(output_path):
        console.print(f"[*] File {output_path} already exists.", style=SUCCESS)
        return 10000

    # Load the image
    image = cv2.imread(image_path)
    if image is None:
        console.print("[!] Error: Unable to load image.", style=DANGER)
        return 500

    # Convert to HSV color space
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Use the user-provided blue color range
    lower_blue = np.array([80, 10, 10])  # Lower bound for blue
    upper_blue = np.array([220, 255, 255])  # Upper bound for blue

    # Create a mask for blue areas
    blue_mask = cv2.inRange(hsv, lower_blue, upper_blue)

    # Apply the mask to the original image
    result = image.copy()
    result[blue_mask > 0] = [255, 255, 255]

    # Convert to grayscale for cropping
    gray = cv2.cvtColor(result, cv2.COLOR_BGR2GRAY)

    # Threshold to binarize the image
    _, binary = cv2.threshold(gray, 240, 255, cv2.THRESH_BINARY_INV)

    # Find contours to determine cropping area
    contours, _ = cv2.findContours(
        binary,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE,
    )

    # Get the bounding box for all non-white areas
    if contours:
        x, y, w, h = cv2.boundingRect(np.vstack(contours))
        cropped_image = result[y : y + h, x : x + w]
        cv2.imwrite(output_path, cropped_image)

        console.print(f"[*] Image processed and saved to {output_path}", style=SUCCESS)
        return 200
    else:
        console.print(
            "[!] No content detected, the image might be completely white.",
            style=DANGER,
        )
        return 200
