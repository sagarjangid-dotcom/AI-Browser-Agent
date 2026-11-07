
import re

from agent.ai_engine import understand_command
from agent.browser import search_google
from modules.scraper import scrape_website
from modules.exporter import export_to_excel


def run_agent():

    print("=" * 45)
    print("          AI BROWSER AGENT")
    print("=" * 45)

    while True:

        command = input("\nEnter your task (or exit): ").strip()

        if command.lower() == "exit":
            print("AI Agent stopped.")
            break

        if not command:
            continue

        try:
            print("\nAI is understanding your command...")

            plan = understand_command(command)

            print("\nAI Generated Plan:\n")
            print(plan)

            approval = input(
                "\nDo you want to execute? (yes/no): "
            ).strip().lower()

            if approval != "yes":
                print("Task cancelled.")
                continue

            # Website scraping and Excel export
            if any(word in command.lower() for word in [
    "scrape", "extract", "website data",
    "main text", "content", "wikipedia"
]):

                match = re.search(r'https?://[^\s]+', command)

                if not match:
                    print("Please provide a valid website URL.")
                    continue

                url = match.group(0).rstrip(".,)")

                print("\nScraping website...")

                data = scrape_website(url)

                if data:
                    export_to_excel(data)
                    print("\nScraping and Excel export completed!")

            # Google search
            elif "search" in command.lower() or "google" in command.lower():

                query = command.lower()

                for word in ["search for", "search", "google", "on google"]:
                    query = query.replace(word, "")

                query = query.strip()

                if query:
                    search_google(query)

            else:
                print("This task is not supported yet.")

        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    run_agent()
