import json
from pathlib import Path

FRAMEWORK = Path(__file__).resolve().parent.parent
active_campaign_path = FRAMEWORK / "active_campaign.json"
summaries_root = FRAMEWORK / "summaries"

def load_json(path, fallback=[]):
    if Path(path).exists():
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return fallback

def generate_summary():
    campaign = load_json(active_campaign_path)
    safe_name = campaign.get("safe_name", "default")
    session_log_path = Path(campaign["paths"]["session_tracker"])
    sessions = load_json(session_log_path)

    if not sessions:
        print("❌ No sessions found.")
        return

    latest = sessions[-1]
    folder = summaries_root / safe_name
    folder.mkdir(parents=True, exist_ok=True)
    session_filename = folder / f"session_{latest['session']:02d}.txt"

    lines = [
        "=== Session Summary ===",
        f"Campaign: {campaign['name']}",
        f"Session #: {latest['session']}",
        f"Date: {latest['date']}",
        f"Summary: {latest['summary']}",
    ]
    if latest['notable_events']:
        lines.append("Events: " + ", ".join(latest['notable_events']))
    if latest['location']:
        lines.append("Locations: " + ", ".join(latest['location']))
    if latest['loot']:
        lines.append("Loot: " + ", ".join(latest['loot']))
    if latest['level_ups']:
        lines.append("Level Ups: " + ", ".join(latest['level_ups']))
    lines.append("========================")

    result = "\n".join(lines)
    print(result)

    with open(session_filename, "w", encoding="utf-8") as f:
        f.write(result + "\n")

if __name__ == "__main__":
    generate_summary()