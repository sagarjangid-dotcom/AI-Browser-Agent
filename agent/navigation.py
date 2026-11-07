
from playwright.sync_api import sync_playwright
from urllib.parse import quote, urlparse


def run_browser_task(command, on_log=None):

    def log(message):
        print(message)
        if on_log:
            on_log(message)

    try:
        command = command.strip()

        if not command:
            raise ValueError("Please enter a browser command.")

        if command.lower().startswith("search "):

            query = command[7:].strip()

            if not query:
                raise ValueError("Search query is empty.")

            url = f"https://html.duckduckgo.com/html/?q={quote(query)}"


        elif command.lower().startswith("open "):

            website = command[5:].strip()

            if not website:
                raise ValueError("Website address is empty.")

            if not website.startswith(("http://", "https://")):
                website = "https://" + website

            parsed = urlparse(website)

            if not parsed.hostname or "." not in parsed.hostname:
                raise ValueError("Please enter a valid website address.")

            url = website

        else:
            raise ValueError(
                "Use: Search Artificial Intelligence "
                "or Open https://www.wikipedia.org"
            )

        with sync_playwright() as p:

            log("Launching browser...")

            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            log("Opening website: " + url)

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            title = page.title()
            current_url = page.url

            if "google.com/sorry" in current_url:
                log("Google CAPTCHA detected.")

                browser.close()

                return {
                    "success": False,
                    "error": "Google CAPTCHA detected. Search could not be completed."
                }

            log("Website opened successfully!")
            log("Extracting website content...")

            headings = page.locator(
                "h1, h2, h3"
            ).all_text_contents()

            paragraphs = page.locator(
                "p"
            ).all_text_contents()

            links = page.locator(
                "a[href]"
            ).evaluate_all("""
                elements => elements.map(a => ({
                    text: a.innerText.trim(),
                    url: a.href
                })).filter(a => a.text && a.url)
            """)

            # Remove empty content and limit output size
            headings = [
                item.strip()
                for item in headings
                if item.strip()
            ][:200]

            paragraphs = [
                item.strip()
                for item in paragraphs
                if item.strip()
            ][:300]

            links = links[:300]

            website_data = {
                "title": title,
                "headings": headings,
                "paragraphs": paragraphs,
                "links": links
            }

            log("Content extraction completed!")
            log("Headings found: " + str(len(headings)))
            log("Paragraphs found: " + str(len(paragraphs)))
            log("Links found: " + str(len(links)))

            browser.close()

            log("Browser closed.")

            return {
                "success": True,
                "title": title,
                "url": current_url,
                "data": website_data,
                "message": "Website content extracted successfully."
            }

    except Exception as e:

        log("Browser Error: " + str(e))

        return {
            "success": False,
            "error": str(e)
        }
