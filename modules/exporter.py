
import pandas as pd
import os


def export_to_excel(data, filename="scraped_data.xlsx"):

    os.makedirs("outputs", exist_ok=True)

    filepath = os.path.join("outputs", filename)

    with pd.ExcelWriter(filepath, engine="openpyxl") as writer:

        # Website title
        title_df = pd.DataFrame({
            "Website Title": [data.get("title", "")]
        })
        title_df.to_excel(
            writer, sheet_name="Website Info", index=False
        )

        # Headings
        headings_df = pd.DataFrame({
            "Headings": data.get("headings", [])
        })
        headings_df.to_excel(
            writer, sheet_name="Headings", index=False
        )

        # Paragraphs
        paragraphs_df = pd.DataFrame({
            "Paragraphs": data.get("paragraphs", [])
        })
        paragraphs_df.to_excel(
            writer, sheet_name="Paragraphs", index=False
        )

        # Links
        links_df = pd.DataFrame(data.get("links", []))
        links_df.to_excel(
            writer, sheet_name="Links", index=False
        )

    print("Excel file created successfully!")
    print("Saved at:", filepath)

    return filepath


if __name__ == "__main__":

    sample_data = {
        "title": "AI Browser Agent Test",
        "headings": ["Introduction", "Features"],
        "paragraphs": [
            "This is a web scraping project.",
            "It extracts website information."
        ],
        "links": [
            {"text": "Google", "url": "https://google.com"},
            {"text": "Wikipedia", "url": "https://wikipedia.org"}
        ]
    }

    export_to_excel(sample_data)
