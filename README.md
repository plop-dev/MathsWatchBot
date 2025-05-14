# MathsWatchBot

A python script that retrieves MathsWatch answers by looking at already submitted homework by logging into users in the same class. **Requires knowledge of users' passwords and ideally usernames beforehand.**

## Features

- **Login**: Authenticate users with their MathsWatch credentials.
- **Extract Answers**: Retrieve answers for assigned work.
- **Get Recent Quizzes**: Fetch the most recent quizzes assigned to a student.
- **Logout**: Securely log out from the MathsWatch platform.
- **Recon**: An separate script that loops through logins and stores them in a json file by class.
- **AI working out**: Since the methods above don't get working out which is often required, I've added gpt-4o to generate the  working out (**will require an OPENAI API account, with enough credits**).

## Installation

1. Clone the repository:

    ```sh
    git clone https://github.com/plop-dev/MathsWatchBot.git
    ```

2. Navigate to the project directory:

    ```sh
    cd MathsWatchBot
    ```

3. Install the required dependencies:

    ```sh
    pip install -r requirements.txt
    ```

4. Add a config file (name it .env):

    ```env
    LOGIN_USERNAME = "User123"
    PASSWORD = "Password123"
    OPENAI_API_KEY=[TOKEN HERE]
    INFO = "bold blue"
    SUCCESS = "bold green"
    DANGER = "bold red"
    ```

5. Run `recon.py` to get a list of users:

    ```sh
    python recon.py
    ```

## License

This project is licensed under the MIT License.

## Contact

For any inquiries, please contact <him@maximec.dev>.

---

<small>this readme is mostly ai so don't judge my ai english.</small>
