
from playwright.sync_api import sync_playwright

browser_state = {}


# ---------------- LOGGING FUNCTION ----------------

def send_log(message, on_log=None):

    print(message)

    if on_log:
        try:
            on_log(message)
        except Exception:
            pass


# ---------------- CLOSE BROWSER ----------------

def close_browser():

    global browser_state

    try:
        browser = browser_state.get("browser")

        if browser:
            browser.close()

    except Exception:
        pass

    try:
        playwright = browser_state.get("playwright")

        if playwright:
            playwright.stop()

    except Exception:
        pass

    browser_state.clear()


# ---------------- FORM FILLING ----------------

def fill_web_form(url, form_data, on_log=None):

    global browser_state

    filled_fields = []
    failed_fields = []

    try:

        close_browser()

        send_log("Starting AI Browser Agent...", on_log)

        playwright = sync_playwright().start()

        browser = playwright.chromium.launch(
            headless=False
        )

        page = browser.new_page()

        browser_state["playwright"] = playwright
        browser_state["browser"] = browser
        browser_state["page"] = page

        send_log("Browser launched successfully.", on_log)

        page.goto(
            url,
            wait_until="domcontentloaded",
            timeout=30000
        )

        send_log(f"Website opened: {url}", on_log)

        # Process each form field
        for field, value in form_data.items():

            filled = False

            send_log(f"Processing field: {field}", on_log)

            try:

                # ---------------- DROPDOWN ----------------

                if isinstance(value, dict) and "select" in value:

                    locator = page.locator(
                        f'select[name="{field}"], '
                        f'select[id="{field}"]'
                    ).first

                    locator.select_option(
                        label=str(value["select"]),
                        timeout=3000
                    )

                    filled = True

                    send_log(
                        f"SUCCESS: Dropdown {field} selected.",
                        on_log
                    )

                # ---------------- CHECKBOX ----------------

                elif isinstance(value, dict) and "checkbox" in value:

                    locator = page.locator(
                        f'input[type="checkbox"][name="{field}"], '
                        f'input[type="checkbox"][id="{field}"]'
                    ).first

                    if value["checkbox"]:
                        locator.check(timeout=3000)
                    else:
                        locator.uncheck(timeout=3000)

                    filled = True

                    send_log(
                        f"SUCCESS: Checkbox {field} updated.",
                        on_log
                    )

                # ---------------- RADIO BUTTON ----------------

                elif isinstance(value, dict) and "radio" in value:

                    radio_value = str(value["radio"])

                    locator = page.locator(
                        f'input[type="radio"][name="{field}"]'
                        f'[value="{radio_value}"]'
                    ).first

                    locator.check(timeout=3000)

                    filled = True

                    send_log(
                        f"SUCCESS: Radio button {field} selected.",
                        on_log
                    )

                # ---------------- NORMAL INPUT ----------------

                else:

                    selectors = [
                        f'input[name="{field}"]',
                        f'textarea[name="{field}"]',
                        f'input[id="{field}"]',
                        f'textarea[id="{field}"]'
                    ]

                    for selector in selectors:

                        try:

                            locator = page.locator(selector).first

                            locator.fill(
                                str(value),
                                timeout=2000
                            )

                            filled = True
                            break

                        except Exception:
                            continue

                    # Label support
                    if not filled:

                        try:

                            page.get_by_label(
                                field,
                                exact=False
                            ).first.fill(
                                str(value),
                                timeout=2000
                            )

                            filled = True

                        except Exception:
                            pass

                    # Placeholder support
                    if not filled:

                        try:

                            page.get_by_placeholder(
                                field,
                                exact=False
                            ).first.fill(
                                str(value),
                                timeout=2000
                            )

                            filled = True

                        except Exception:
                            pass

                    if filled:

                        send_log(
                            f"SUCCESS: {field} filled successfully.",
                            on_log
                        )

                if filled:

                    filled_fields.append(field)

                else:

                    failed_fields.append(field)

                    send_log(
                        f"FAILED: Could not fill {field}.",
                        on_log
                    )

            except Exception as e:

                failed_fields.append(field)

                send_log(
                    f"ERROR: {field}: {str(e)}",
                    on_log
                )

        # Final result
        if failed_fields:

            send_log(
                "Form filling completed with some errors.",
                on_log
            )

        else:

            send_log(
                "All form fields filled successfully.",
                on_log
            )

        send_log(
            "Waiting for user approval before submission.",
            on_log
        )

        return {
            "success": len(failed_fields) == 0,
            "filled": filled_fields,
            "failed": failed_fields,
            "message": "Form filling completed."
        }

    except Exception as e:

        send_log(
            f"Browser automation error: {str(e)}",
            on_log
        )

        close_browser()

        return {
            "success": False,
            "filled": filled_fields,
            "failed": [
                field for field in form_data
                if field not in filled_fields
            ],
            "message": str(e)
        }


# ---------------- FORM SUBMISSION ----------------

def submit_form(url=None, form_data=None, on_log=None):

    try:

        send_log(
            "User approved form submission.",
            on_log
        )

        page = browser_state.get("page")

        if page is None or page.is_closed():

            send_log(
                "ERROR: Browser session not found.",
                on_log
            )

            return {
                "success": False,
                "message": "Browser session not found."
            }

        send_log(
            "Searching for submit button...",
            on_log
        )

        submit_button = page.locator(
            'button[type="submit"], input[type="submit"]'
        ).first

        submit_button.click(timeout=5000)

        send_log(
            "Submit button clicked.",
            on_log
        )

        try:

            page.wait_for_load_state(
                "domcontentloaded",
                timeout=10000
            )

        except Exception:

            send_log(
                "Page navigation wait completed or timed out.",
                on_log
            )

        send_log(
            "Submission action completed.",
            on_log
        )

        return {
            "success": True,
            "message": "Form submitted successfully."
        }

    except Exception as e:

        send_log(
            f"Submission error: {str(e)}",
            on_log
        )

        return {
            "success": False,
            "message": str(e)
        }

    finally:

        close_browser()

        send_log(
            "Browser session closed.",
            on_log
        )
