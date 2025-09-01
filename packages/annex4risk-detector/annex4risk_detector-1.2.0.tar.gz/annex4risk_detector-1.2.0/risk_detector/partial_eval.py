from __future__ import annotations
from typing import Any, Set, Tuple

TRUE, FALSE, UNKNOWN = "TRUE", "FALSE", "UNKNOWN"


def collect_vars(node: Any, keys: Set[str] | None = None) -> Set[str]:
    keys = keys or set()
    if isinstance(node, dict):
        if set(node.keys()) == {"var"} and isinstance(node.get("var"), str):
            keys.add(node["var"])
        else:
            for v in node.values():
                collect_vars(v, keys)
    elif isinstance(node, list):
        for it in node:
            collect_vars(it, keys)
    return keys


def _value_or_unknown(x: Any, answers: dict) -> Tuple[bool, Any]:
    if isinstance(x, dict) and "var" in x and isinstance(x["var"], str):
        k = x["var"]
        return (k not in answers), answers.get(k)
    if isinstance(x, (str, int, float, bool, type(None), list, dict)):
        if isinstance(x, dict) and len(x.keys()) == 1 and next(iter(x)) not in {"var"}:
            s = eval3(x, answers)
            if s == TRUE:
                return (False, True)
            if s == FALSE:
                return (False, False)
            return (True, None)
        return (False, x)
    return (True, None)


def _all_states(states):
    has_true = any(s == TRUE for s in states)
    has_false = any(s == FALSE for s in states)
    has_unknown = any(s == UNKNOWN for s in states)
    return has_true, has_false, has_unknown


def eval3(node: Any, answers: dict) -> str:
    if not isinstance(node, dict) or len(node) != 1:
        return UNKNOWN

    op, args = next(iter(node.items()))

    if op == "and" and isinstance(args, list):
        child_states = [eval3(a, answers) if isinstance(a, dict) else (TRUE if a else FALSE) for a in args]
        has_true, has_false, has_unknown = _all_states(child_states)
        if has_false:
            return FALSE
        if not has_unknown:
            return TRUE
        return UNKNOWN

    if op == "or" and isinstance(args, list):
        child_states = [eval3(a, answers) if isinstance(a, dict) else (TRUE if a else FALSE) for a in args]
        has_true, has_false, has_unknown = _all_states(child_states)
        if has_true:
            return TRUE
        if not has_unknown:
            return FALSE
        return UNKNOWN

    if op in {"!", "not"} and isinstance(args, (list, dict, bool)):
        x = args[0] if isinstance(args, list) else args
        state = eval3(x, answers) if isinstance(x, dict) else (TRUE if not x else FALSE)
        if state == TRUE:
            return FALSE
        if state == FALSE:
            return TRUE
        return UNKNOWN

    if op in {"==", "===", "="} and isinstance(args, list) and len(args) == 2:
        u1, v1 = _value_or_unknown(args[0], answers)
        u2, v2 = _value_or_unknown(args[1], answers)
        if not u1 and not u2:
            return TRUE if v1 == v2 else FALSE
        return UNKNOWN

    if op in {"!=", "!=="} and isinstance(args, list) and len(args) == 2:
        u1, v1 = _value_or_unknown(args[0], answers)
        u2, v2 = _value_or_unknown(args[1], answers)
        if not u1 and not u2:
            return TRUE if v1 != v2 else FALSE
        return UNKNOWN

    if op in {"<", ">", "<=", ">="} and isinstance(args, list) and len(args) == 2:
        u1, v1 = _value_or_unknown(args[0], answers)
        u2, v2 = _value_or_unknown(args[1], answers)
        if not u1 and not u2 and isinstance(v1, (int, float)) and isinstance(v2, (int, float)):
            if op == "<":
                return TRUE if v1 < v2 else FALSE
            if op == ">":
                return TRUE if v1 > v2 else FALSE
            if op == "<=":
                return TRUE if v1 <= v2 else FALSE
            if op == ">=":
                return TRUE if v1 >= v2 else FALSE
        return UNKNOWN

    if op == "in" and isinstance(args, list) and len(args) == 2:
        u1, v1 = _value_or_unknown(args[0], answers)
        u2, v2 = _value_or_unknown(args[1], answers)
        if not u1 and not u2 and isinstance(v2, list):
            return TRUE if v1 in v2 else FALSE
        return UNKNOWN

    if op == "var":
        key = args if isinstance(args, str) else (args[0] if isinstance(args, list) else None)
        if isinstance(key, str) and key in answers:
            return UNKNOWN
        return UNKNOWN

    return UNKNOWN
