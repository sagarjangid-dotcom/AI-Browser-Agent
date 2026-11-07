import os
from dotenv import load_dotenv
from google import genai

# Load API key
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("Gemini API key not found in .env file")

# Initialize Gemini
client = genai.Client(api_key=API_KEY)


def understand_command(user_command):

    prompt = f"""
    You are an intelligent AI browser automation agent.

    Understand the user's command and create a simple,
    safe browser automation plan.

    Rules:
    1. Return clear numbered steps.
    2. Identify which website needs to be opened.
    3. Identify what action needs to be performed.
    4. Never perform purchases or submit forms without user approval.
    5. Keep the plan simple and understandable.

    User command: {user_command}
    """

    response = client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents=prompt
    )

    return response.text


if __name__ == "__main__":

    command = input("Enter your browser task: ")

    try:
        result = understand_command(command)

        print("\nAI Generated Plan:\n")
        print(result)

    except Exception as e:
        print("\nError:", e)