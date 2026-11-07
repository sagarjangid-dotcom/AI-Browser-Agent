from playwright.sync_api import sync_playwright


def open_website(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        page.goto(url, wait_until="domcontentloaded")

        print("Website opened:", page.title())

        input("Press Enter to close browser...")
        browser.close()


def search_google(query):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()

        print("Opening Google...")
        page.goto("https://www.google.com")

        print("Searching:", query)
        page.locator("textarea[name='q'], input[name='q']").first.fill(query)
        page.keyboard.press("Enter")

        page.wait_for_load_state("domcontentloaded")

        print("Search completed!")
        print("Page title:", page.title())

        input("Press Enter to close browser...")
        browser.close()


if __name__ == "__main__":
    search_google("Artificial Intelligence tutorials")