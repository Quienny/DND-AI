import json
from pathlib import Path
import requests

# === Load active campaign ===
framework = Path("C:/Users/Quint/Desktop/DND_AI_DM/SillyTavern/data/default-user/DND_Campaign_Framework")

with open(framework / "active_campaign.json", encoding="utf-8") as f:
    campaign = json.load(f)

paths = campaign["paths"]
safe_name = campaign["safe_name"]

def load(path):
    p = Path(path)
    if p.exists():
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return []

# === Build lorebook entries ===
lorebook_entries = []

for char in load(paths["characters"]):
    name = char.get("character") or char.get("Character Name")
    if name:
        lorebook_entries.append({
            "title": name,
            "keys": [name],
            "content": f"{name}, a level {char.get('level')} {char.get('race')} {char.get('class')}."
        })

for npc in load(paths["npcs"]):
    name = npc.get("name")
    if name:
        lorebook_entries.append({
            "title": name,
            "keys": [name],
            "content": npc.get("description", "An NPC of interest.")
        })

for item in load(paths["items"]):
    name = item.get("name")
    if name:
        lorebook_entries.append({
            "title": name,
            "keys": [name],
            "content": item.get("description", "An item of note.")
        })

for faction in load(paths["factions"]):
    name = faction.get("name")
    if name:
        lorebook_entries.append({
            "title": name,
            "keys": [name],
            "content": faction.get("description", "A known faction.")
        })

for town in load(paths["towns"]):
    name = town.get("name")
    if name:
        lorebook_entries.append({
            "title": name,
            "keys": [name],
            "content": town.get("description", "A known location.")
        })

for lore in load(paths["lorebooks"]):
    name = lore.get("title")
    if name:
        lorebook_entries.append({
            "title": name,
            "keys": lore.get("keys", [name]),
            "content": lore.get("content", "")
        })

# === Save combined lorebook ===
lorebook_path = framework / "lorebooks" / safe_name / "combined_lorebook.json"
lorebook_path.parent.mkdir(parents=True, exist_ok=True)
with open(lorebook_path, "w", encoding="utf-8") as f:
    json.dump(lorebook_entries, f, indent=2)

# === Direct API injection into SillyTavern memory ===
print("📡 Sending campaign memory directly to SillyTavern...")

url = "http://127.0.0.1:8687/memory/update"
data = {
    "char_name": "Dungeon Master",
    "memory": f"Current Campaign: {campaign['name']}\n\nYou are the Dungeon Master for this world."
}

try:
    r = requests.post(url, json=data, headers={"token": "token"})

    if r.ok:
        print("✅ Campaign memory injected into Dungeon Master successfully.")
    else:
        print(f"⚠️ Memory API responded with status {r.status_code}: {r.text}")
except Exception as e:
    print(f"❌ Failed to connect to SillyTavern memory API: {e}")
