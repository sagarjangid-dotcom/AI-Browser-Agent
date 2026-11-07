from playwright.sync_api import sync_playwright

print("1. Import successful", flush=True)

try:
    print("2. Starting Playwright...", flush=True)

    with sync_playwright() as p:
        print("3. Playwright started!", flush=True)

        browser = p.chromium.launch(headless=False)
        print("4. Browser launched!", flush=True)

        browser.close()

except BaseException as e:
    print("ERROR:", repr(e), flush=True)
