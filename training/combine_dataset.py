import json
from pathlib import Path


REAL_DATA = Path("training/data/sft_dataset.jsonl")
SYNTHETIC_DATA = Path("training/data/synthetic_sft.jsonl")
OUTPUT = Path("training/data/final_sft_dataset.jsonl")


def load_jsonl(path):
    with path.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def main():
    real = load_jsonl(REAL_DATA)
    synthetic = load_jsonl(SYNTHETIC_DATA)

    combined = real + synthetic

    with OUTPUT.open("w", encoding="utf-8") as f:
        for example in combined:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")

    print("Dataset combination complete.")
    print(f"Real examples:      {len(real)}")
    print(f"Synthetic examples: {len(synthetic)}")
    print(f"Total examples:     {len(combined)}")
    print(f"Saved to:            {OUTPUT}")


if __name__ == "__main__":
    main()