"""Simple coverage check to ensure rules have questions."""
import yaml
from pathlib import Path
from .question_builder import needed_feature_keys


def load_yaml(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f) or []


def check_coverage(rules_path: Path, features_path: Path, questions_path: Path):
    rules = load_yaml(rules_path)
    features = {f["key"]: f for f in load_yaml(features_path)}
    questions = load_yaml(questions_path)
    keys = needed_feature_keys([type("R", (), {"condition": r["condition"]}) for r in rules])
    missing = [k for k in keys if k not in features]
    missing_questions = [k for k in keys if k not in {q["feature_key"] for q in questions} and not features.get(k, {}).get("required")]
    return missing, missing_questions
