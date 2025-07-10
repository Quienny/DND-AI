
import random
import re
import json
from pathlib import Path

TABLES_PATH = Path(__file__).resolve().parent / "random_tables.json"

def roll(dice_str):
    match = re.match(r'(\d*)d(\d+)([+-]\d+)?', dice_str.replace(" ", ""))
    if not match:
        return {"error": "Invalid dice format", "input": dice_str}

    num = int(match.group(1)) if match.group(1) else 1
    die = int(match.group(2))
    mod = int(match.group(3)) if match.group(3) else 0

    rolls = [random.randint(1, die) for _ in range(num)]
    total = sum(rolls) + mod

    return {
        "roll": dice_str,
        "rolls": rolls,
        "modifier": mod,
        "total": total
    }

def roll_table(table_name):
    if not TABLES_PATH.exists():
        return {"error": "No table file found."}

    with open(TABLES_PATH, "r", encoding="utf-8") as f:
        tables = json.load(f)

    table = tables.get(table_name)
    if not table:
        return {"error": f"No table named '{table_name}'"}

    choice = random.choice(table)
    return {
        "table": table_name,
        "result": choice
    }
