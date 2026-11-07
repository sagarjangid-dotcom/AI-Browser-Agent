
import streamlit as st
import re
import os
import json
import pandas as pd
from agent.workflow import run_multi_step_task

from agent.ai_engine import understand_command
from agent.navigation import run_browser_task
from modules.scraper import scrape_website
from modules.exporter import export_to_excel
from modules.form_filler import fill_web_form, submit_form
from modules.history import save_form_history


# ---------------- HELPER FUNCTIONS ----------------

def validate_form_value(value):

    if isinstance(value, (str, int, float, bool)):
        return True

    if isinstance(value, dict):

        if len(value) != 1:
            return False

        key, item = next(iter(value.items()))

        if key == "select":
            return isinstance(item, str)

        if key == "checkbox":
            return isinstance(item, bool)

        if key == "radio":
            return isinstance(item, str)

    return False


def validate_form_details(details):

    return (
        isinstance(details, dict)
        and bool(details)
        and all(
            isinstance(key, str)
            and key.strip()
            and validate_form_value(value)
            for key, value in details.items()
        )
    )

def execute_navigation(command):

    logs = []
    log_placeholder = st.empty()

    st.session_state.pop("navigation_data", None)
    st.session_state.pop("navigation_excel", None)

    def update_log(message):
        logs.append(message)
        log_placeholder.code(
            "\n".join(logs),
            language="text"
        )

    try:

        result = run_multi_step_task(
            command,
            on_log=update_log
        )

        st.session_state["navigation_logs"] = logs
        st.session_state["navigation_result"] = result

        if result.get("success") and result.get("data"):

            os.makedirs("outputs", exist_ok=True)

            filepath = export_to_excel(
                result["data"],
                filename="navigation_data.xlsx"
            )

            st.session_state["navigation_data"] = result["data"]
            st.session_state["navigation_excel"] = filepath

    except Exception as e:

        update_log(f"Error: {e}")

        st.session_state["navigation_logs"] = logs

        st.session_state["navigation_result"] = {
            "success": False,
            "error": str(e),
            "steps": []
        }


# ---------------- PAGE CONFIGURATION ----------------

st.set_page_config(
    page_title="AI Browser Agent",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Browser Agent")
st.subheader("Intelligent Web Automation System")

st.write(
    "Give a command, review the AI plan, "
    "approve it, and automate your browser task."
)

st.divider()


# ---------------- AI COMMAND CENTER ----------------

st.header("🧠 AI Command Center")

command = st.text_area(
    "Enter your browser task:",
    placeholder=(
        "Scrape https://en.wikipedia.org/wiki/Artificial_intelligence\n"
        "Search Artificial Intelligence\n"
        "Open https://www.wikipedia.org"
    ),
    height=120
)

if st.button("Generate AI Plan", type="primary"):

    if not command.strip():

        st.warning("Please enter a command.")

    else:

        with st.spinner("Gemini AI is understanding your command..."):

            try:

                plan = understand_command(command)

                st.session_state["plan"] = plan
                st.session_state["command"] = command

            except Exception as e:

                st.error(f"AI Error: {e}")


if "plan" in st.session_state:

    st.subheader("AI Generated Plan")

    st.markdown(st.session_state["plan"])

    st.warning("Review the AI plan before execution.")

    if st.button("Approve & Execute"):

        task = st.session_state["command"].strip()
        task_lower = task.lower()

        # Browser Navigation
        if task_lower.startswith(("search ", "open ")):

            with st.spinner("Executing browser navigation..."):

                execute_navigation(task)

            result = st.session_state["navigation_result"]

            if result["success"]:

                st.success("Browser task completed successfully!")

                st.write("**Page Title:**", result["title"])
                st.write("**Website URL:**", result["url"])

            else:

                st.error(
                    result.get("error", "Browser navigation failed.")
                )

        # Website Scraping
        elif any(word in task_lower for word in [
            "scrape", "extract", "website data",
            "main text", "content"
        ]):

            match = re.search(
                r'https?://[^\s]+',
                task
            )

            if not match:

                st.error("Please provide a valid website URL.")

            else:

                url = match.group(0).rstrip(".,)")

                with st.spinner("Scraping website..."):

                    data = scrape_website(url)

                if data:

                    os.makedirs("outputs", exist_ok=True)

                    filepath = export_to_excel(data)

                    st.session_state["scraped_data"] = data
                    st.session_state["excel_path"] = filepath

                    st.success("Website scraped successfully!")

                else:

                    st.error("Website scraping failed.")

        else:

            st.info(
                "This command is not supported yet. "
                "Use Search, Open, Scrape, or the Form Filling section."
            )


# ---------------- BROWSER NAVIGATION PANEL ----------------

st.divider()

st.header("🌐 Browser Navigation & Search")

st.write(
    "Open a website or search the web using Playwright."
)

navigation_command = st.text_input(
    "Enter Navigation Command",
    placeholder="Search Artificial Intelligence"
)

nav_col1, nav_col2 = st.columns(2)

with nav_col1:

    if st.button("🔍 Search / Open Website", type="primary"):

        if not navigation_command.strip():

            st.warning("Please enter a command.")

        else:

            with st.spinner("Browser is executing your command..."):

                execute_navigation(navigation_command)

with nav_col2:

    if st.button("Clear Navigation Results"):

        st.session_state.pop("navigation_logs", None)
        st.session_state.pop("navigation_result", None)


# Navigation Results
if "navigation_result" in st.session_state:

    nav_result = st.session_state["navigation_result"]

    st.subheader("Navigation Result")

    if nav_result["success"]:

        st.success("Browser task completed successfully!")

        st.write("**Page Title:**", nav_result["title"])
        st.write("**Website URL:**", nav_result["url"])

    else:

        st.error(
            nav_result.get("error", "Navigation failed.")
        )


# Navigation Logs
# Multi-Step Workflow Results
if "navigation_result" in st.session_state:

    workflow = st.session_state["navigation_result"]

    if workflow.get("steps"):

        st.subheader("⚙️ Multi-Step Execution Status")

        for step in workflow["steps"]:

            col1, col2 = st.columns([4, 1])

            with col1:
                st.write(
                    f"**Step {step['step']}:** "
                    f"{step['command']}"
                )

                if step.get("url"):
                    st.caption(step["url"])

            with col2:

                if step["success"]:
                    st.success("Completed")
                else:
                    st.error("Failed")

# ---------------- NAVIGATION DATA DASHBOARD ----------------

if "navigation_data" in st.session_state:

    data = st.session_state["navigation_data"]

    st.divider()

    st.header("📊 Website Content Extraction Dashboard")

    st.write("**Website Title:**", data.get("title", "Not Available"))

    col1, col2, col3 = st.columns(3)

    col1.metric(
        "Total Headings",
        len(data.get("headings", []))
    )

    col2.metric(
        "Total Paragraphs",
        len(data.get("paragraphs", []))
    )

    col3.metric(
        "Total Links",
        len(data.get("links", []))
    )

    with st.expander("📌 Website Headings"):

        for heading in data.get("headings", []):
            st.write("•", heading)

    with st.expander("📝 Website Paragraphs"):

        for paragraph in data.get("paragraphs", []):
            st.write(paragraph)

    with st.expander("🔗 Website Links"):

        for link in data.get("links", []):
            st.write(
                link.get("text", ""),
                link.get("url", "")
            )

    filepath = st.session_state.get("navigation_excel")

    if filepath and os.path.exists(filepath):

        with open(filepath, "rb") as file:

            st.download_button(
                label="📥 Download Navigation Excel Report",
                data=file.read(),
                file_name="navigation_data.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
            
# ---------------- SCRAPED DATA ----------------

if "scraped_data" in st.session_state:

    data = st.session_state["scraped_data"]

    st.divider()

    st.header("📊 Scraped Website Data")

    st.write("**Website Title:**", data["title"])

    col1, col2, col3 = st.columns(3)

    col1.metric("Headings", len(data["headings"]))
    col2.metric("Paragraphs", len(data["paragraphs"]))
    col3.metric("Links", len(data["links"]))

    with st.expander("View Headings"):

        for heading in data["headings"]:
            st.write("•", heading)

    with st.expander("View Paragraphs"):

        for paragraph in data["paragraphs"]:
            st.write(paragraph)

    with st.expander("View Links"):

        for link in data["links"]:
            st.write(link["text"], link["url"])

    filepath = st.session_state["excel_path"]

    with open(filepath, "rb") as file:

        st.download_button(
            label="📥 Download Excel Report",
            data=file.read(),
            file_name="scraped_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )


# ---------------- FORM FILLING AUTOMATION ----------------

st.divider()

st.header("📝 AI Form Filling Automation")

st.write(
    "Enter a website URL and form details. "
    "The agent fills the fields and waits for your approval."
)

form_url = st.text_input(
    "Form Website URL",
    placeholder="https://www.selenium.dev/selenium/web/web-form.html"
)

form_details = st.text_area(
    "Form Details (JSON format)",
    value='{\n  "my-text": "Sagar Jangid",\n  "my-password": "Test123",\n  "my-textarea": "Testing AI Browser Agent"\n}',
    height=180
)

with st.expander("Advanced Form JSON Examples"):

    st.write("**Dropdown:**")
    st.code('{"country": {"select": "India"}}', language="json")

    st.write("**Checkbox:**")
    st.code('{"agree": {"checkbox": true}}', language="json")

    st.write("**Radio Button:**")
    st.code('{"gender": {"radio": "Male"}}', language="json")


# ---------------- FILL FORM BUTTON ----------------

if st.button("Fill Form", type="primary"):

    if not form_url.strip():

        st.error("Please enter a website URL.")

    elif not form_url.startswith(("http://", "https://")):

        st.error("URL must start with http:// or https://")

    else:

        try:

            details = json.loads(form_details)

            if not validate_form_details(details):

                st.error(
                    "Invalid form details. Use text, numbers, "
                    "booleans or supported select/checkbox/radio objects."
                )

            else:

                st.session_state["form_url"] = form_url
                st.session_state["form_details"] = details

                execution_logs = []
                log_placeholder = st.empty()

                def update_log(message):

                    execution_logs.append(message)

                    log_placeholder.code(
                        "\n".join(execution_logs),
                        language="text"
                    )

                with st.spinner("Running browser automation..."):

                    update_log("AI Browser Agent started.")

                    result = fill_web_form(
                        form_url,
                        details,
                        on_log=update_log
                    )

                    update_log("Form automation process finished.")

                st.session_state["form_result"] = result
                st.session_state["execution_logs"] = execution_logs

                history_file = save_form_history(
                    form_url,
                    details,
                    result
                )

                st.session_state["history_file"] = history_file

                if result["success"]:

                    st.success("Form filling completed successfully!")

                else:

                    st.error(
                        result.get("message", "Form filling failed.")
                    )

                st.success("Form history saved successfully!")

        except json.JSONDecodeError:

            st.error("Invalid JSON. Please check your form details.")

        except Exception as e:

            st.error(f"Form error: {e}")


# ---------------- REAL-TIME EXECUTION LOGS ----------------

if "execution_logs" in st.session_state:

    st.divider()

    st.header("📋 Form Execution Logs")

    for message in st.session_state["execution_logs"]:

        st.write("•", message)


# ---------------- FORM RESULT ----------------

if "form_result" in st.session_state:

    result = st.session_state["form_result"]

    if result["success"]:

        st.success("Form filling process completed!")

        st.write(
            "**Successfully filled fields:**",
            result["filled"]
        )

        st.write(
            "**Fields not found:**",
            result["failed"]
        )

        if not result["failed"]:

            st.warning(
                "Review all the filled details in the browser "
                "before submitting."
            )

            if st.button("Approve & Submit Form"):

                submit_logs = []
                submit_log_placeholder = st.empty()

                def update_submit_log(message):

                    submit_logs.append(message)

                    submit_log_placeholder.code(
                        "\n".join(submit_logs),
                        language="text"
                    )

                with st.spinner("Submitting approved form..."):

                    submit_result = submit_form(
                        st.session_state["form_url"],
                        st.session_state["form_details"],
                        on_log=update_submit_log
                    )

                st.session_state["submit_logs"] = submit_logs

                if submit_result["success"]:

                    st.success(submit_result["message"])

                    history_file = save_form_history(
                        st.session_state["form_url"],
                        st.session_state["form_details"],
                        {
                            "success": True,
                            "filled": result["filled"],
                            "failed": [],
                            "status": "Submitted"
                        }
                    )

                    st.session_state["history_file"] = history_file

                    st.session_state.pop("form_result", None)
                    st.session_state.pop("form_url", None)
                    st.session_state.pop("form_details", None)

                else:

                    st.error(
                        "Submission failed: "
                        + submit_result["message"]
                    )

        else:

            st.error(
                "Some fields were not found. "
                "Please correct the field names before submission."
            )

    else:

        st.error(
            result.get("message", "Form filling failed.")
        )


# ---------------- SUBMISSION LOGS ----------------

if "submit_logs" in st.session_state:

    st.divider()

    st.header("📤 Form Submission Logs")

    for message in st.session_state["submit_logs"]:

        st.write("•", message)


# ---------------- FORM HISTORY ----------------

st.divider()

st.header("📁 Form History & Data Storage")

st.write(
    "Your form filling records are stored in an Excel file."
)

history_path = os.path.join(
    "outputs",
    "form_history.xlsx"
)

if os.path.exists(history_path):

    history_df = pd.read_excel(history_path)

    st.metric(
        "Total Form Records",
        len(history_df)
    )

    st.dataframe(
        history_df,
        use_container_width=True
    )

    with open(history_path, "rb") as file:

        st.download_button(
            label="📥 Download Form History",
            data=file.read(),
            file_name="form_history.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

else:

    st.info(
        "No form history available yet. Fill a form to create history."
    )


# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "AI Browser Agent | B.Tech CSE AI & DS Major Project"
)
