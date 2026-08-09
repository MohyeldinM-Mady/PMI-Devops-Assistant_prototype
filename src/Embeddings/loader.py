import json

INPUT_PATH = "data/processed/knowledge_base.json"


def load_documents():
    with open(INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)