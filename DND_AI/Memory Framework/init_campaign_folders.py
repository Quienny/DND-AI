import os
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: init_campaign_folders.py <campaign_name>")
    sys.exit(1)

campaign_name = sys.argv[1]
root_dir = Path(__file__).resolve().parent.parent
framework_dir = root_dir / "Memory Framework"

folders = {
    "characters": {
        "filename": "characters.json",
        "default": [
            {
                "player": "Player 1",
                "Character Name": "New Character",
                "class": "Fighter",
                "race": "Human",
                "level": 1,
                "notes": ""
            },
            {
                "player": "Player 2",
                "Character Name": "New Character",
                "class": "Wizard",
                "race": "Elf",
                "level": 1,
                "notes": "Copy and paste this template to add more players."
            }
        ]
    },
    "npcs": {"filename": "npcs.json", "default": []},
    "items": {"filename": "items.json", "default": []},
    "towns": {"filename": "towns.json", "default": []},
    "factions": {"filename": "factions.json", "default": []},
    "lorebooks": {"filename": "lorebooks.json", "default": []},
    "session_tracker": {"filename": "session_tracker.json", "default": []},
    "sessions": {"filename": "sessions.json", "default": []},
    "summaries": {"filename": "summaries.json", "default": []}
}

for folder, config in folders.items():
    path = framework_dir / folder / campaign_name
    path.mkdir(parents=True, exist_ok=True)
    file_path = path / config["filename"]
    if not file_path.exists():
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(config["default"], f, indent=2)
        print(f"Created: {file_path}")
    else:
        print(f"Exists:  {file_path}")

# === Memory folder creation with party name extraction ===
memory_dir = framework_dir / "memory" / campaign_name
memory_dir.mkdir(parents=True, exist_ok=True)
memory_json = memory_dir / "memory.json"

if not memory_json.exists():
    characters_path = framework_dir / "characters" / campaign_name / "characters.json"
    if characters_path.exists():
        with open(characters_path, encoding="utf-8") as f:
            characters = json.load(f)
        party_names = [c.get("Character Name") or c.get("character") for c in characters if c.get("Character Name") or c.get("character")]
    else:
        party_names = []

    default_memory = {
        "campaign": campaign_name,
        "session": 1,
        "current_location": "Unknown",
        "party": party_names,
        "active_goals": [],
        "npcs": {},
        "items": {}
    }

    with open(memory_json, "w", encoding="utf-8") as f:
        json.dump(default_memory, f, indent=2)
    print(f"Created memory.json with party: {party_names}")
else:
    print("Exists: memory.json")

print(f"✅ Campaign '{campaign_name}' memory structure verified.")
