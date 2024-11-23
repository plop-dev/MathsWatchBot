# MathsWatchBot

A python script that retrieves MathsWatch answers by looking at already submitted homework by logging into users in the same class. **Requires knowledge of users' passwords and ideally usernames beforehand.**

## Features

- **Login**: Authenticate users with their MathsWatch credentials.
- **Extract Answers**: Retrieve answers for assigned work.
- **Get Recent Quizzes**: Fetch the most recent quizzes assigned to a student.
- **Logout**: Securely log out from the MathsWatch platform.
- **Recon**: An separate script that loops through logins and stores them in a json file by class.

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/yourusername/MathsWatchBot.git
    ```

2. Navigate to the project directory:

    ```sh
    cd MathsWatchBot
    ```

3. Install the required dependencies:
    you'll get errors for depedencies that aren't installed anyways

## Usage

1. **Get Cookies**:

    ```py
    from getcookies import getcookies
    cookies = getcookies("username", "password")
    ```

2. **Login**:

    ```py
    from login import login
    status_code = login(cookies["connect.sid"], cookies["_csrf"], "username", "password")
    ```

3. **Extract Answers**:

    ```py
    from extractanswers import extractanswers
    answers = extractanswers(cookies["connect.sid"], cookies["_csrf"], "quiz_id")
    ```

4. **Get Recent Quizzes**:

    ```py
    from getrecent import getrecent
    recent_quiz = getrecent(cookies["connect.sid"], cookies["_csrf"])
    ```

5. **Logout**:

    ```py
    from logout import logout
    status_code = logout(cookies["connect.sid"], cookies["_csrf"])
    ```

## File Structure

- `getcookies.py`: Contains the function to get cookies for authentication.
- `login.py`: Handles user login.
- `extractanswers.py`: Extracts answers for assigned work.
- `getrecent.py`: Retrieves recent quizzes.
- `logout.py`: Logs out the user.
- `main.py`: Main script to run the bot.
- `recon.py`: Script for reconnaissance tasks.
- `.gitignore`: Specifies files and directories to be ignored by Git.

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact <him@maximec.dev>.
