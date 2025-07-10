import os
import json
from pathlib import Path
from datetime import datetime
import re

# === CONFIG ===
BASE_DIR = Path(r"C:/Users/Quint/Desktop/DND_AI_DM/SillyTavern/data/default-user")
FRAMEWORK_DIR = BASE_DIR / "DND_Campaign_Framework"
CAMPAIGN_META_PATH = FRAMEWORK_DIR / "active_campaign.json"

def load_json(path, fallback=[]):
    if Path(path).exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return fallback

def save_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def append_unique(path, entry, key="name"):
    data = load_json(path)
    if not any(d.get(key) == entry.get(key) for d in data):
        data.append(entry)
        save_json(path, data)

def compress_summary(messages, limit=50):
    assistant_lines = [m['text'] for m in messages if m.get("sender") == "assistant"]
    joined = " ".join(assistant_lines[:limit])
    return re.sub(r'\s+', ' ', joined).strip()[:800]

def extract_entities(messages):
    text_block = " ".join(m['text'].lower() for m in messages)
    def findall(keywords):
        return list(set([w for kw in keywords for w in re.findall(rf"\b\w*{kw}\w*\b", text_block)]))
    return {
        "text_block": text_block,
        "npcs": findall(["npc", "innkeep", "barkeep", "merchant"]),
        "locations": findall(["village", "cave", "city", "keep", "temple"]),
        "items": findall(["sword", "potion", "amulet", "artifact"]),
        "loot": findall(["gold", "loot", "treasure"]),
        "level_ups": findall(["level up", "leveled up", "gained a level"]),
        "events": findall(["killed", "defeated", "rescued", "ambushed"]),
        "players": list(set(w for m in messages if m['sender'] == 'user' for w in re.findall(r'\b[A-Z][a-z]+\b', m['text'])))
    }

def validate_campaign_paths(meta):
    campaign_dir = Path(meta["paths"]["campaign_dir"])
    milestones = Path(meta["paths"]["milestones"])
    pdf_path = FRAMEWORK_DIR / "campaigns" / meta["name"] / "campaign.pdf"

    if not campaign_dir.exists() or not milestones.exists():
        print("❌ Missing extracted narration or milestones for this campaign.")
        return False
    if not pdf_path.exists():
        print("❌ Original campaign.pdf not found.")
        return False
    return True

def process_sessions():
    # Load campaign context
    if not CAMPAIGN_META_PATH.exists():
        print("❌ No active_campaign.json found. Use campaign_loader.py to set one.")
        return

    campaign = load_json(CAMPAIGN_META_PATH)
    if not validate_campaign_paths(campaign):
        return

    PATHS = campaign["paths"]
    tracker = load_json(PATHS["session_tracker"])
    characters = load_json(PATHS["characters"])
    last_path_file = Path(PATHS["session_tracker"]).parent / "last_processed.json"
    last_path = load_json(last_path_file, {})

    chat_log_dir = BASE_DIR / "chats" / "Dungeon Master"
    session_num = len(tracker) + 1

    for file in sorted(chat_log_dir.glob("*.jsonl")):
        if str(file) == last_path.get("last_processed"):
            continue
        with open(file, 'r', encoding='utf-8') as f:
            messages = [json.loads(line) for line in f if line.strip()]

        date = file.stem.replace('_', '-')
        summary = compress_summary(messages)
        meta = extract_entities(messages)
        text_block = meta.pop("text_block")

        session_log = {
            "session": session_num,
            "date": date,
            "summary": summary,
            "level_ups": meta["level_ups"],
            "loot": meta["loot"],
            "location": meta["locations"],
            "notable_events": meta["events"],
            "notes": []
        }

        tracker.append(session_log)
        save_json(PATHS["session_tracker"], tracker)
        save_json(last_path_file, {"last_processed": str(file)})
        session_num += 1

        for loc in meta["locations"]:
            append_unique(PATHS["lorebooks"], {"title": loc.title(), "keys": [loc], "content": f"A known location: {loc.title()}."})
        for npc in meta["npcs"]:
            append_unique(PATHS["npcs"], {"name": npc.title(), "description": "NPC mentioned in gameplay."})
        for item in meta["items"]:
            append_unique(PATHS["items"], {"name": item.title(), "description": "Magical or notable item."})
        for town in meta["locations"]:
            append_unique(PATHS["towns"], {"name": town.title(), "region": "", "description": "A mentioned town or place."})
        if "cult" in text_block or "guild" in text_block:
            append_unique(PATHS["factions"], {"name": "Unknown Faction", "description": "Mentioned in passing."})

        for player in meta["players"]:
            existing = next((c for c in characters if c["character"] == player), None)
            if not existing:
                characters.append({
                    "player": "Unknown",
                    "character": player,
                    "class": "",
                    "level": 1,
                    "race": "",
                    "notes": "Auto-added from session log.",
                    "last_updated": date
                })
            else:
                existing["last_updated"] = date
        save_json(PATHS["characters"], characters)

        print(f"✓ Parsed session: {file.name}")

if __name__ == "__main__":
    process_sessions()