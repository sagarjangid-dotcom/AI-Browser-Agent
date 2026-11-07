
import os
import json
from datetime import datetime
import pandas as pd


def save_form_history(url, form_data, result):

    os.makedirs("outputs", exist_ok=True)

    filepath = os.path.join("outputs", "form_history.xlsx")

    # Sensitive information ko Excel mein save nahi karna
    sensitive_words = [
        "password",
        "token",
        "secret",
        "api_key",
        "authorization",
        "otp"
    ]

    safe_details = {
        key: value
        for key, value in form_data.items()
        if not any(word in key.lower() for word in sensitive_words)
    }

    # Status identify karna
    status = result.get("status")

    if not status:
        status = "Filled" if result.get("success") else "Failed"

    # History record
    history_record = {
        "Date & Time": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "Website URL": url,
        "Form Details": json.dumps(safe_details),
        "Filled Fields": ", ".join(result.get("filled", [])),
        "Failed Fields": ", ".join(result.get("failed", [])),
        "Status": status
    }

    new_record = pd.DataFrame([history_record])

    # Existing Excel history read karna
    if os.path.exists(filepath):

        old_records = pd.read_excel(filepath)

        updated_records = pd.concat(
            [old_records, new_record],
            ignore_index=True
        )

    else:
        updated_records = new_record

    # Excel file update karna
    updated_records.to_excel(filepath, index=False)

    return filepath
