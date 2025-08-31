"""Aggregate matched rules to a final category."""
from . import __init__  # noqa: F401

PRIORITY = ["prohibited", "high_risk", "limited_risk", "minimal_risk"]

def classify(rules, answers):
    matched = []
    for rule in rules:
        if rule["matched"]:
            matched.append(rule)
    category = "minimal_risk"
    for cat in PRIORITY:
        if any(r["category"] == cat for r in matched):
            category = cat
            break
    score = sum(r.get("weight", 1.0) for r in matched if r["category"] == category)
    legal_refs = sorted({ref for r in matched for ref in r.get("legal_refs", [])})
    exception = any(r["category"] == "conditional" for r in matched)
    return {
        "category": category,
        "score": score,
        "legal_refs": legal_refs,
        "exception_applied": exception,
        "matched_rules": [r["id"] for r in matched],
    }
