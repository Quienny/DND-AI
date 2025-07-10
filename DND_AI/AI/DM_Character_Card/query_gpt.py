import os
import json
from datetime import datetime
import openai
import copy

# === CONFIG ===
API_KEY = "API key here"
client = openai.OpenAI(api_key=API_KEY)

# === PATH SETUP ===
BASE_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_PATH, "..", ".."))
import sys
sys.path.append(os.path.join(ROOT_DIR, "Piper"))
from piper_tts import speak

FRAMEWORK_DIR = os.path.join(ROOT_DIR, "Memory Framework")
ACTIVE_CAMPAIGN_FILE = os.path.join(FRAMEWORK_DIR, "active_campaign.json")

def get_active_campaign():
    try:
        with open(ACTIVE_CAMPAIGN_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                name = data.get("safe_name") or data.get("name")
                paths = data.get("paths", {})
                return name, paths
            elif isinstance(data, str):
                return data.strip(), {}
    except:
        pass
    return "Unknown", {}

def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return None

def save_json(path, data):
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"[ERROR] Could not save to {path}: {e}")

def load_campaign_data(campaign, custom_paths={}):
    context = {
        "system_info": {
            "campaign": campaign,
            "timestamp": datetime.now().isoformat()
        }
    }

    data_types = {
        "characters": "characters.json",
        "npcs": "npcs.json",
        "items": "items.json",
        "lorebooks": "lorebooks.json",
        "session_tracker": "session_tracker.json",
        "summaries": "summaries.json",
        "towns": "towns.json",
        "factions": "factions.json"
    }

    for key, filename in data_types.items():
        if key in custom_paths:
            full_path = custom_paths[key]
        else:
            full_path = os.path.join(FRAMEWORK_DIR, key, campaign, filename)

        context[key] = load_json(full_path)

    return context

def write_context_changes(old_ctx, new_ctx, custom_paths):
    for key in ["characters", "summaries", "npcs", "factions", "items", "towns", "lorebooks", "session_tracker"]:
        if key in new_ctx and new_ctx[key] != old_ctx.get(key):
            target_path = custom_paths.get(key) or os.path.join(FRAMEWORK_DIR, key, campaign, f"{key}.json")
            save_json(target_path, new_ctx[key])

    # Part-specific summaries
    if "summaries" in new_ctx:
        parts_dir = os.path.join(FRAMEWORK_DIR, "summaries", campaign)
        for summary in new_ctx["summaries"]:
            if isinstance(summary, dict) and "part" in summary:
                part_path = os.path.join(parts_dir, f"summary_part_{int(summary['part']):02d}.json")
                save_json(part_path, [summary])

def query_gpt(context, prompt):
    system_prompt = """
You are the Dungeon Master and sole narrator for this D&D campaign.

🧠 Your duties:
- Request players to make ability checks with their dice when an action is not gauranteed to occur
- Make sure you ask players to run dice checks
- Narrate scenes using context, memory, and summaries
- Keep responses short: 1–3 sentences unless setting a new scene or narrating a dramatic moment
- Narrate based on what the player says their character does or says — keep it simple and direct
- If the player says, "Character does X", respond with "You do X. Here's the outcome..."
- Expect the player to speak in third person, but respond using second person ("you")
- Do not over-describe or add dramatic flair unless the situation calls for it
- Imagine new NPCs, events, or consequences as needed based on context
- If it's combat or turn-based mode, call on the character by name at the start of the response and wait for their next action
- Assume the speaking character remains active until a new name is given
- Update JSON memory where needed (e.g., session log, NPC state, location, tone)

🎲 Dice Usage Policy:
- Use `dice_engine.roll()` whenever an outcome is uncertain
- DO NOT show dice results unless the player asks directly
- Just narrate the result naturally:
  - ❌ "You rolled a 12."
  - ✅ "The guard narrows his eyes but says nothing."

🧪 Manual Rolls:
- If the player types `.roll 1d20+2 Drog`, process it and save the outcome in memory under `"last_roll"`

🎭 You are not an assistant. You are the voice and logic of the game world. Do not break character.
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Context:\n{json.dumps(context, indent=2)}\n\nPrompt:\n{prompt}"}
            ],
            temperature=0.3,
            max_tokens=2048
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"[ERROR] GPT request failed: {e}"

def extract_context_update(response_text):
    try:
        if "```json" in response_text:
            json_block = response_text.split("```json")[1].split("```")[0]
        else:
            json_block = response_text
        return json.loads(json_block)
    except:
        return None

if __name__ == "__main__":
    campaign, custom_paths = get_active_campaign()
    context = load_campaign_data(campaign, custom_paths)
    print(f"\n🧠 GPT-4o Memory Engine initialized for campaign: {campaign}\n")

    while True:
        try:
            user_prompt = input("Enter your prompt (or type 'exit' to quit):\n> ")
            if user_prompt.lower() in ("exit", "quit"):
                break

            original = copy.deepcopy(context)
            reply = query_gpt(context, user_prompt)
            print("\n🧠 GPT-4o Memory Engine Response:\n")
            print(reply)
            speak(reply)
            print()

            updated = extract_context_update(reply)
            if updated:
                context.update(updated)
                write_context_changes(original, context, custom_paths)

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"\n[Error] {e}\n")
