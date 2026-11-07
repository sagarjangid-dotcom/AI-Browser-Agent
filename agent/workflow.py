import re
from agent.navigation import run_browser_task


def run_multi_step_task(command, on_log=None):

    def log(message):
        print(message)
        if on_log:
            on_log(message)

    # Split commands using "then" or a new line
    commands = re.split(
        r"\s+\bthen\b\s+|\n+",
        command.strip(),
        flags=re.IGNORECASE
    )

    commands = [
        item.strip()
        for item in commands
        if item.strip()
    ]

    if not commands:
        return {
            "success": False,
            "error": "No browser tasks provided.",
            "steps": []
        }

    steps = []
    last_result = None

    for index, task in enumerate(commands, start=1):

        task_lower = task.lower()

        if not task_lower.startswith(("open ", "search ")):
            error = (
                f"Step {index} is unsupported: {task}. "
                "Use Open or Search commands."
            )

            log(error)

            return {
                "success": False,
                "error": error,
                "steps": steps
            }

        log(f"Starting Step {index}: {task}")

        result = run_browser_task(
            task,
            on_log=log
        )

        step_info = {
            "step": index,
            "command": task,
            "success": result.get("success", False),
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "error": result.get("error", "")
        }

        steps.append(step_info)
        last_result = result

        if not result.get("success"):

            log(f"Step {index} failed. Workflow stopped.")

            return {
                "success": False,
                "error": result.get(
                    "error",
                    f"Step {index} failed."
                ),
                "steps": steps,
                "title": step_info["title"],
                "url": step_info["url"]
            }

        log(f"Step {index} completed successfully.")

    log("All browser steps completed!")

    return {
        "success": True,
        "title": last_result.get("title", ""),
        "url": last_result.get("url", ""),
        "data": last_result.get("data"),
        "steps": steps,
        "message": "Multi-step workflow completed successfully."
    }