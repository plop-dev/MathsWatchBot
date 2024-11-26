import ollama
from ollama import ChatResponse
from rich.console import Console
from utils import convert_latex_to_unicode
import base64

console = Console()


def encode_image(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")


base64_image = encode_image("./questions/2041_cropped.png")

response: ChatResponse = ollama.chat(
    model="llama3.2-vision",
    messages=[
        {
            "role": "system",
            "content": "You only provide working out for provided questions; no answers. Do not provide any text; only latex. You will receive 1 or 2 questions labelled as 'a' or 'b'; answer both. Do not provide the question; only the steps inbetween. Provide between 2-4 steps of working out. Don't include \\begin or \\align or \\\\ or boxed in the latex.",
        },
        {
            "role": "user",
            "content": "What is the working out for this question?",
            "images": [
                r"C:\Users\[]\Documents\Dev\Python\MathsWatchBot\questions\2041_cropped.png"
            ],
        },
    ],
)

print(response["message"]["content"].strip(), "\n\n\n")
print(convert_latex_to_unicode(response["message"]["content"].strip()), "\n\n\n")
