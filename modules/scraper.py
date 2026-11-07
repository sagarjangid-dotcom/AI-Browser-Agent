
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup


def scrape_website(url):

    print("Opening website:", url)

    try:
        with sync_playwright() as p:

            browser = p.chromium.launch(headless=True)
            page = browser.new_page()

            page.goto(
                url,
                wait_until="domcontentloaded",
                timeout=30000
            )

            print("Website loaded successfully!")

            # Get website HTML
            html = page.content()

            # Parse HTML
            soup = BeautifulSoup(html, "html.parser")

            # Extract title
            title = soup.title.string.strip() if soup.title and soup.title.string else "No title"

            # Extract headings
            headings = [
                h.get_text(strip=True)
                for h in soup.find_all(["h1", "h2", "h3"])
                if h.get_text(strip=True)
            ]

            # Extract paragraphs
            paragraphs = [
                p.get_text(" ", strip=True)
                for p in soup.find_all("p")
                if p.get_text(strip=True)
            ]

            # Extract links
            links = [
                {
                    "text": a.get_text(strip=True),
                    "url": a.get("href")
                }
                for a in soup.find_all("a", href=True)
                if a.get_text(strip=True)
            ]

            browser.close()

            result = {
                "title": title,
                "headings": headings,
                "paragraphs": paragraphs,
                "links": links
            }

            return result

    except Exception as e:
        print("Scraping Error:", e)
        return None


if __name__ == "__main__":

    website = input("Enter website URL: ").strip()

    if not website.startswith(("http://", "https://")):
        website = "https://" + website

    data = scrape_website(website)

    if data:
        print("\nWEBSITE TITLE:")
        print(data["title"])

        print("\nHEADINGS:")
        for heading in data["headings"]:
            print("-", heading)

        print("\nPARAGRAPHS:")
        for paragraph in data["paragraphs"][:5]:
            print("-", paragraph)

        print("\nTOTAL LINKS:", len(data["links"]))
