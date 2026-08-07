# PMI Data Collection

Phase 1 of PMI — data collection from GitHub.

## Setup
1. Install dependencies: `pip install -r requirements.txt`
2. Copy `.env.example` to `.env` and fill in your GitHub credentials.
3. Run the data collector: `python -m src.collect`

## Output
Collected data will be saved as JSON files in the `data/` directory (e.g., `data/commits.json`).

## Note
This is Phase 1 of a multi-phase pipeline (Phase 2 = knowledge extraction, downstream).
