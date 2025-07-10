import json
import os
import sys
import traceback
from pathlib import Path
from datetime import datetime

try:
    # === CONFIG ===
    FRAMEWORK_DIR = Path(__file__).resolve().parent
    CAMPAIGN_DIR = FRAMEWORK_DIR / "campaigns"
    ACTIVE_CAMPAIGN_PATH = FRAMEWORK_DIR / "active_campaign.json"
    CRASH_LOG_DIR = FRAMEWORK_DIR / "crash_logs"

    def set_active_campaign(campaign_name):
        safe_name = campaign_name.replace(" ", "_")
        active = {
            "name": campaign_name,
            "safe_name": safe_name,
            "paths": {
                "characters": str(FRAMEWORK_DIR / "characters" / safe_name / "characters.json"),
                "npcs": str(FRAMEWORK_DIR / "npcs" / safe_name / "npcs.json"),
                "items": str(FRAMEWORK_DIR / "items" / safe_name / "items.json"),
                "towns": str(FRAMEWORK_DIR / "towns" / safe_name / "towns.json"),
                "factions": str(FRAMEWORK_DIR / "factions" / safe_name / "factions.json"),
                "lorebooks": str(FRAMEWORK_DIR / "lorebooks" / safe_name / "lorebooks.json"),
                "session_tracker": str(FRAMEWORK_DIR / "session_tracker" / safe_name / "session_tracker.json"),
                "sessions": str(FRAMEWORK_DIR / "sessions" / safe_name / "sessions.json"),
                "campaign_dir": str(CAMPAIGN_DIR / campaign_name / "extracted"),
                "milestones": str(CAMPAIGN_DIR / campaign_name / "extracted" / "milestones.json"),
                "rules": str(FRAMEWORK_DIR / "rules")
            }
        }

        with open(ACTIVE_CAMPAIGN_PATH, 'w', encoding='utf-8') as f:
            json.dump(active, f, indent=2)
        print(f"\n Campaign set: {campaign_name}")

    if __name__ == "__main__":
        if len(sys.argv) > 1:
            name = sys.argv[1]
        else:
            print("Enter campaign name to activate:")
            name = input("> ")
        set_active_campaign(name)

except Exception as e:
    print("Error Error in campaign_loader:")
    traceback.print_exc()
    sys.exit(1)