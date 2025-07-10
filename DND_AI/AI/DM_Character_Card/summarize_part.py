import json
from pathlib import Path
import re

# === CONFIG ===
FRAMEWORK = Path("C:/Users/Quint/Desktop/DND_AI_DM/SillyTavern/data/default-user/DND_Campaign_Framework")
ACTIVE_CAMPAIGN_PATH = FRAMEWORK / "active_campaign.json"
SUMMARIES_ROOT = FRAMEWORK / "summaries"

def load_json(path, fallback=None):
    if not path.exists():
        return fallback
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def extract_part_number(filename):
    match = re.search(r'part_(\d+)\.json', filename)
    return int(match.group(1)) if match else None

def build_summary_entry(part_number, content):
    return {
        "part": part_number,
        "title": f"Part {part_number:02d}",
        "summary": f"(Placeholder summary for Part {part_number:02d})",
        "highlights": [],
        "notes": []
    }

def main():
    # === Load Active Campaign Info ===
    campaign = load_json(ACTIVE_CAMPAIGN_PATH)
    if not campaign:
        print("❌ active_campaign.json not found or unreadable.")
        return

    safe_name = campaign.get("safe_name", "default")
    campaign_parts_path = Path(campaign["paths"]["campaign_dir"])
    summary_output_path = SUMMARIES_ROOT / safe_name
    summary_output_path.mkdir(parents=True, exist_ok=True)

    # === Find All Part Files ===
    part_files = sorted([f for f in campaign_parts_path.glob("part_*.json")], key=lambda f: extract_part_number(f.name))

    for part_file in part_files:
        part_num = extract_part_number(part_file.name)
        if part_num is None:
            continue

        summary_file = summary_output_path / f"summary_part_{part_num:02d}.json"
        if summary_file.exists():
            continue  # ✅ Already exists

        # Create summary template
        content = load_json(part_file, {})
        summary_log = [build_summary_entry(part_num, content)]
        save_json(summary_file, summary_log)
        print(f"📄 Created summary_part_{part_num:02d}.json")

    print("✅ Summary scaffolding complete.")

if __name__ == "__main__":
    main()
