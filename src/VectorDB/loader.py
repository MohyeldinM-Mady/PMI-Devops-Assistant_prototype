import json

from src.config import PROCESSED_DIR

INPUT_PATH = PROCESSED_DIR / "embedded_documents.json"


def load_embedded_documents():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)
