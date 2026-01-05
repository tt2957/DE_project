# expand_seeds.py

import random
import json
from pathlib import Path

RAW_MATCH_DIR = Path("../data/raw/matches")
SEED_FILE = Path("../seed_players.txt")

MAX_SEEDS = 50
EXPANSION_PER_MATCH = 1


def is_bot(player_id: str) -> bool:
    return player_id.startswith("ai.") if player_id else False


def load_existing_seeds():
    if not SEED_FILE.exists():
        return set()

    with open(SEED_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())


def save_new_seeds(seeds):
    with open(SEED_FILE, "w", encoding="utf-8") as f:
        for s in sorted(seeds):
            f.write(s + "\n")


def extract_players_from_match(match_path):
    with open(match_path, "r", encoding="utf-8") as f:
        match = json.load(f)

    players = []

    for item in match["included"]:
        if item["type"] == "participant":
            stats = item["attributes"]["stats"]
            player_id = stats.get("playerId")
            if player_id and not is_bot(player_id):
                players.append(player_id)

    return players


def expand_seeds():
    seeds = load_existing_seeds()
    print(f"Current seeds: {len(seeds)}")

    if len(seeds) >= MAX_SEEDS:
        print("Seed limit reached.")
        return

    new_seeds = set(seeds)

    for match_path in RAW_MATCH_DIR.glob("*.json"):
        players = extract_players_from_match(match_path)
        random.shuffle(players)

        for pid in players[:EXPANSION_PER_MATCH]:
            if pid not in new_seeds:
                new_seeds.add(pid)
                print(f"Added seed: {pid}")

            if len(new_seeds) >= MAX_SEEDS:
                break

        if len(new_seeds) >= MAX_SEEDS:
            break

    save_new_seeds(new_seeds)
    print(f"Total seeds after expansion: {len(new_seeds)}")


if __name__ == "__main__":
    expand_seeds()
