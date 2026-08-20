import json
import random
from pathlib import Path


INPUT = Path("training/data/final_sft_dataset.jsonl")
TRAIN_OUTPUT = Path("training/data/train.jsonl")
VAL_OUTPUT = Path("training/data/validation.jsonl")

random.seed(42)


def load_dataset():
    with INPUT.open("r", encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def save_dataset(path, data):
    with path.open("w", encoding="utf-8") as f:
        for example in data:
            f.write(json.dumps(example, ensure_ascii=False) + "\n")


def main():
    data = load_dataset()

    random.shuffle(data)

    split_index = int(len(data) * 0.9)

    train_data = data[:split_index]
    validation_data = data[split_index:]

    save_dataset(TRAIN_OUTPUT, train_data)
    save_dataset(VAL_OUTPUT, validation_data)

    print("Dataset split complete.")
    print(f"Total examples:      {len(data)}")
    print(f"Training examples:   {len(train_data)}")
    print(f"Validation examples: {len(validation_data)}")
    print(f"Training file:       {TRAIN_OUTPUT}")
    print(f"Validation file:     {VAL_OUTPUT}")


if __name__ == "__main__":
    main()