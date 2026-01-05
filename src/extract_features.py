# extract_features.py

import json
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "matches"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

def load_match_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"⚠️ [Error] 파일이 깨져있어 스킵합니다: {path}")
        print(f"   에러 내용: {e}")
        return None


def extract_participants(match_json):
    participants = []

    for item in match_json["included"]:
        if item["type"] == "participant":
            stats = item["attributes"]["stats"]
            participants.append(stats)

    return participants


def is_bot(stats: dict) -> bool:
    player_id = stats.get("playerId")
    if not player_id:
        return False
    return player_id.startswith("ai.")


def extract_match_features(match_json, participants):
    attr = match_json["data"]["attributes"]

    total_players = len(participants)
    bot_count = sum(1 for p in participants if is_bot(p))

    return {
        "match_id": match_json["data"]["id"],
        "created_at": attr.get("createdAt"),
        "duration": attr.get("duration"),
        "map_name": attr.get("mapName"),
        "game_mode": attr.get("gameMode"),
        "total_players": total_players,
        "bot_count": bot_count,
        "bot_ratio": bot_count / total_players if total_players else 0,
    }


def extract_distribution_features(participants):
    human_players = [p for p in participants if not is_bot(p)]

    kills = [p.get("kills", 0) for p in human_players]
    survival = [p.get("timeSurvived", 0) for p in human_players]

    return {
        "avg_kills": sum(kills) / len(kills) if kills else 0,
        "max_kills": max(kills) if kills else 0,
        "kill_std": float(pd.Series(kills).std()) if len(kills) > 1 else 0,
        "avg_survival_time": sum(survival) / len(survival) if survival else 0,
        "survival_std": float(pd.Series(survival).std()) if len(survival) > 1 else 0,
    }


def extract_features_from_match(match_json):
    participants = extract_participants(match_json)

    features = {}
    features.update(extract_match_features(match_json, participants))
    features.update(extract_distribution_features(participants))

    return features


def process_all_matches(raw_dir, output_csv):
    rows = []

    for path in Path(raw_dir).glob("*.json"):
        match_json = load_match_json(path)
        if match_json is None: # 깨진 파일이면 다음 파일로
            continue
        rows.append(extract_features_from_match(match_json))

    df = pd.DataFrame(rows)
    Path(output_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_csv, index=False)

    print(f"Saved {len(df)} rows to {output_csv}")



if __name__ == "__main__":
    process_all_matches(
        raw_dir=RAW_DIR,
        output_csv=PROCESSED_DIR / "matches.csv",
    )

