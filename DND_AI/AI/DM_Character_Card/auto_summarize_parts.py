import json
import re
from pathlib import Path
import openai
from datetime import datetime

def load_json(path, fallback=None):
    if not path.exists():
        return fallback
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# === CONFIG ===
API_KEY = "your_real_api_key_here"  # Replace before running
client = openai.OpenAI(api_key=API_KEY)

FRAMEWORK = Path("C:/Users/Quint/Desktop/DND_AI_DM/SillyTavern/data/default-user/DND_Campaign_Framework")
ACTIVE_CAMPAIGN_PATH = FRAMEWORK / "active_campaign.json"
SUMMARIES_ROOT = FRAMEWORK / "summaries"

campaign = load_json(ACTIVE_CAMPAIGN_PATH)
if not campaign:
    print(" active_campaign.json not found.")
    exit(1)

safe_name = campaign["safe_name"]
LOG_FILE = SUMMARIES_ROOT / safe_name / "summary_log.txt"
SUMMARIES_JSON = Path(campaign["paths"].get("summaries", ""))

def log(message):
    timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S]")
    with open(LOG_FILE, "a", encoding="utf-8") as log_file:
        log_file.write(f"{timestamp} {message}\n")
    try:
        print(message)
    except UnicodeEncodeError:
        print(message.encode("ascii", "ignore").decode())

def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

def extract_part_number(filename):
    match = re.search(r'part_(\d+)\.json', filename)
    return int(match.group(1)) if match else None

def is_placeholder(entry):
    return entry.get("summary", "").lower().startswith("(placeholder")

def summarize_part(context, part_text, part_number):
    messages = [
        {
            "role": "system",
            "content": (
                "You are a D&D memory summarizer. You create structured summaries for each part of a long-running campaign. "
                "Use the provided context and new content to expand the summary for the current part. "
                "Tie in previous events if relevant, otherwise focus on the new material. Be concise but clear."
            )
        },
        {
            "role": "user",
            "content": (
                "Previous summaries:\n"
                + json.dumps(context, indent=2)
                + "\n\nNew Part " + str(part_number) + " Content:\n"
                + json.dumps(part_text, indent=2)
                + "\n\nReturn a JSON object with:\n"
                "- part: the part number\n"
                "- title: a one-line title\n"
                "- summary: a concise but rich paragraph summary\n"
                "- highlights: a list of key events\n"
                "- notes: extra GM notes or unresolved threads"
            )
        }
    ]
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=messages,
        temperature=0.5,
        max_tokens=1500
    )
    return json.loads(response.choices[0].message.content)

def main():
    campaign_dir = Path(campaign["paths"]["campaign_dir"])
    summary_dir = SUMMARIES_ROOT / safe_name
    summary_dir.mkdir(parents=True, exist_ok=True)

    part_files = sorted([f for f in campaign_dir.glob("part_*.json")], key=lambda x: extract_part_number(x.name))
    full_summaries = []

    for i, part_file in enumerate(part_files):
        part_number = extract_part_number(part_file.name)
        part_content = load_json(part_file)
        summary_path = summary_dir / f"summary_part_{part_number:02d}.json"

        prior_summaries = []
        for j in range(1, part_number):
            p = summary_dir / f"summary_part_{j:02d}.json"
            prior = load_json(p, [])
            prior_summaries.extend(e for e in prior if not is_placeholder(e))

        new_entry = summarize_part(prior_summaries, part_content, part_number)
        save_json(summary_path, [new_entry])
        log(f"📄 Created summary_part_{part_number:02d}.json")

        full_summaries.append(new_entry)

    # Overwrite the real summaries.json file with full list
    if SUMMARIES_JSON:
        save_json(SUMMARIES_JSON, full_summaries)
        log(f"🧠 Updated {SUMMARIES_JSON.name} with full summaries list.")

    log("✅ All parts summarized.")

if __name__ == "__main__":
    main()