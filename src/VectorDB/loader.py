import json

INPUT_PATH = "data/processed/embedded_documents.json"

def load_embedded_documents():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

