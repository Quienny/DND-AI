import json
from pathlib import Path

try:
    active_path = Path("C:/Users/Quint/Desktop/DND_AI_DM/SillyTavern/data/default-user/DND_Campaign_Framework/active_campaign.json")
    if not active_path.exists():
        print("❌ active_campaign.json not found.")
        exit(1)

    active = json.load(open(active_path, encoding="utf-8"))
    char_path = Path(active['paths']['characters'])

    if not char_path.exists():
        char_path.parent.mkdir(parents=True, exist_ok=True)
        with open(char_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=2)
        print(f"✅ Created empty characters.json at: {char_path}")
    else:
        print(f"✅ characters.json already exists at: {char_path}")

except Exception as e:
    print(f"❌ Error: {e}")
    exit(1)