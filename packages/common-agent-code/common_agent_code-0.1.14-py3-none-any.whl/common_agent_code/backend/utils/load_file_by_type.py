import os
import pandas as pd
import json 

def load_file_by_type(file_path):
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".csv":
        return pd.read_csv(file_path), "df"

    elif ext == ".json":
        with open(file_path, "r") as f:
            return json.load(f), "json"

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read(), "text"

    elif ext == ".xlsx":
        return pd.read_excel(file_path), "df"

    elif ext == ".pdf":
        from PyPDF2 import PdfReader
        reader = PdfReader(file_path)
        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])
        return text, "pdf_text"

    return f"[Unsupported file format: {ext}]", "unsupported"
