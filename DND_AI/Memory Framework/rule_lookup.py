
import json
from pathlib import Path

def load_json(path, fallback=[]):
    if Path(path).exists():
        with open(path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return fallback

def load_rule(campaign, rule_type, name=None):
    rules_dir = Path(campaign["paths"]["rules"])
    rule_file = rules_dir / f"{rule_type}.json"
    if not rule_file.exists():
        return None

    data = load_json(rule_file)
    if name is None:
        return data

    if isinstance(data, dict) and "results" in data:
        data = data["results"]

    for rule in data:
        if rule.get("name", "").lower() == name.lower():
            return rule
    return None
