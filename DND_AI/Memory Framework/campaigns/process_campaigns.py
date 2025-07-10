import json
import re
import unicodedata
from pathlib import Path

# === CONFIG ===
CAMPAIGNS_DIR = Path(__file__).parent
CHAPTER_MIN_LENGTH = 200
FORCE = False

def clean_text(text):
    text = unicodedata.normalize("NFKD", text)
    text = re.sub(r"(?<=[a-zA-Z])N{2,}(?=[a-zA-Z])", "", text)
    text = re.sub(r'-\s*\n\s*', '', text)
    text = re.sub(r'\n{2,}', '\n\n', text)
    text = re.sub(r'\s{3,}', ' ', text)
    text = re.sub(r'\n +', '\n', text)
    return text.strip()

def extract_text_blocks_from_txt(txt_path):
    with open(txt_path, "r", encoding="utf-8") as f:
        full_text = f.read()
    lines = full_text.splitlines()
    text_by_chapter = {}
    buffer = []
    current_title = "Prologue"
    chapter_counter = 1

    chapter_pattern = re.compile(r"^(chapter|part|section|act)\s*\d*", re.IGNORECASE)

    for line in lines:
        line_clean = line.strip()
        if chapter_pattern.match(line_clean.lower()):
            if buffer and len(" ".join(buffer)) > CHAPTER_MIN_LENGTH:
                cleaned = clean_text("\n".join(buffer))
                text_by_chapter[f"Chapter {chapter_counter}"] = cleaned
                chapter_counter += 1
            buffer = []
        buffer.append(line_clean)

    if buffer and len(" ".join(buffer)) > CHAPTER_MIN_LENGTH:
        cleaned = clean_text("\n".join(buffer))
        text_by_chapter[f"Chapter {chapter_counter}"] = cleaned

    return text_by_chapter

def extract_milestones(text_by_chapter):
    milestones = []
    milestone_pattern = re.compile(
        r"(gain|reach|advance|attain|achieve)\s.*?(\d+(st|nd|rd|th)?\slevel)", re.IGNORECASE)

    for title, text in text_by_chapter.items():
        matches = milestone_pattern.findall(text)
        for match in matches:
            full_phrase = " ".join(match).strip()
            milestones.append({
                "chapter": title,
                "trigger": full_phrase,
                "raw": full_phrase
            })
    return milestones

def process_campaign_folder(folder: Path):
    print(f"📘 Processing: {folder.name}")
    extracted_dir = folder / "extracted"
    extracted_dir.mkdir(exist_ok=True)

    processed_flag = folder / "processed.txt"
    if processed_flag.exists() and not FORCE:
        print(f"  ⏩ Skipping (already processed)")
        return

    txt_files = list(folder.glob("*.txt"))
    if not txt_files:
        print("  ❌ No .txt file found.")
        return
    txt = txt_files[0]

    text_blocks = extract_text_blocks_from_txt(txt)
    if not text_blocks:
        print("  ❌ Failed to extract text.")
        return

    chapter_count = 0
    for i, (title, text) in enumerate(text_blocks.items(), 1):
        safe_title = re.sub(r'[^a-zA-Z0-9_]', '_', title.lower())[:40]
        fname = f"chapter_{i}_{safe_title}.json"
        with open(extracted_dir / fname, 'w', encoding='utf-8') as f:
            json.dump({"title": title, "content": text}, f, indent=2, ensure_ascii=False)
        chapter_count += 1

    milestones = extract_milestones(text_blocks)
    with open(extracted_dir / "milestones.json", 'w', encoding='utf-8') as f:
        json.dump(milestones, f, indent=2, ensure_ascii=False)

    with open(processed_flag, 'w') as f:
        f.write("processed")

    print(f"  ✅ Saved {chapter_count} chapters, {len(milestones)} milestones")

def main():
    for folder in CAMPAIGNS_DIR.iterdir():
        if folder.is_dir():
            process_campaign_folder(folder)

if __name__ == "__main__":
    main()
