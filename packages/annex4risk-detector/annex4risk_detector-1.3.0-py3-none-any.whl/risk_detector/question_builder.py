"""Build question list from rules and features."""
from typing import Dict, List, Optional, Set
from .evaluators.jsonlogic_eval import evaluate_rule


def _walk_jsonlogic(node, keys: Set[str]):
    if isinstance(node, dict):
        for k, v in node.items():
            if k == "var" and isinstance(v, str):
                keys.add(v)
            else:
                _walk_jsonlogic(v, keys)
    elif isinstance(node, list):
        for item in node:
            _walk_jsonlogic(item, keys)


def needed_feature_keys(rules) -> Set[str]:
    keys: Set[str] = set()
    for r in rules:
        _walk_jsonlogic(r.condition, keys)
    return keys


def build_questions(
    rules, features: Dict[str, any], questions_db, answers: Optional[Dict[str, any]] = None
) -> List[any]:
    """Return ordered list of questions filtered by used features and gating."""
    keys = needed_feature_keys(rules)
    keys |= {k for k, f in features.items() if getattr(f, "required", False)}

    answers = answers or {}
    ordered: List[any] = []
    for q in questions_db:
        if q.feature_key not in keys:
            continue
        if q.gating and not evaluate_rule(q.gating, answers):
            continue
        ordered.append(q)
    ordered.sort(key=lambda q: getattr(q, "priority", 0))
    return ordered
