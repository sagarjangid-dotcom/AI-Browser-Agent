import os
import time
from dotenv import load_dotenv
from google import genai

load_dotenv(".env", override=True)

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("API key not found!")
else:
    client = genai.Client(api_key=api_key)

    for attempt in range(3):
        try:
            print(f"Connecting... Attempt {attempt + 1}")

            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents="Say hello in one sentence."
            )

            print("Gemini Connected Successfully!")
            print(response.text)
            break

        except Exception as e:
            print("Connection Failed:", e)

            if attempt < 2:
                print("Retrying after 10 seconds...")
                time.sleep(10)
            else:
                print("Please try again later.")
