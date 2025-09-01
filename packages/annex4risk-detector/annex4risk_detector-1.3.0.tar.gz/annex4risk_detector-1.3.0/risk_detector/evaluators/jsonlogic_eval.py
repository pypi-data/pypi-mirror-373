"""Evaluate a subset of JSONLogic expressions.

Supported operators and behavior:

* Comparison: ``==``, ``!=``, ``>``, ``<``, ``>=``, ``<=``
* Logic: ``and``, ``or``, ``!``
* Membership: ``in`` and ``contains`` (return ``False`` on type errors)
* Array quantifiers: ``all``/``some`` expect a list and yield ``False``
  otherwise
* Conditional: ``if`` (``cond ? then : else``)
* Strings: ``startswith`` (prefix match) and ``lower`` (case-folding,
  ``None`` passthrough)
* Presence: ``missing`` returns keys absent from the provided data
* Variables: ``var`` resolves dotted keys like ``user.name`` and accepts an
  optional default ``{"var": ["key", default]}``
"""


def _eval(node, data):
    """Recursively evaluate a JSONLogic node."""
    if isinstance(node, dict):
        op, vals = next(iter(node.items()))
        if op == "==":
            return _eval(vals[0], data) == _eval(vals[1], data)
        if op == "!=":
            return _eval(vals[0], data) != _eval(vals[1], data)
        if op == ">":
            return _eval(vals[0], data) > _eval(vals[1], data)
        if op == "<":
            return _eval(vals[0], data) < _eval(vals[1], data)
        if op == ">=":
            return _eval(vals[0], data) >= _eval(vals[1], data)
        if op == "<=":
            return _eval(vals[0], data) <= _eval(vals[1], data)
        if op == "and":
            return all(_eval(v, data) for v in vals)
        if op == "or":
            return any(_eval(v, data) for v in vals)
        if op == "!":
            return not _eval(vals, data)
        if op == "in":
            try:
                return _eval(vals[0], data) in _eval(vals[1], data)
            except Exception:
                # On invalid container types, default to False
                return False
        if op == "contains":
            container = _eval(vals[0], data)
            item = _eval(vals[1], data)
            try:
                return item in container
            except Exception:
                # Non-iterable containers yield False
                return False
        if op == "all":
            arr, cond = _eval(vals[0], data), vals[1]
            if not isinstance(arr, list):
                # JSONLogic expects a list; non-lists cannot satisfy ``all``
                return False
            return all(_eval(cond, {**data, "it": it}) for it in arr)
        if op == "some":
            arr, cond = _eval(vals[0], data), vals[1]
            if not isinstance(arr, list):
                # Non-list input results in False
                return False
            return any(_eval(cond, {**data, "it": it}) for it in arr)
        if op == "if":
            cond, then, els = vals
            return _eval(then, data) if _eval(cond, data) else _eval(els, data)
        if op == "startswith":
            s = _eval(vals[0], data)
            prefix = _eval(vals[1], data)
            try:
                return str(s).startswith(str(prefix))
            except Exception:
                # Cast failures or non-string inputs return False
                return False
        if op == "lower":
            val = _eval(vals[0], data) if isinstance(vals, list) else _eval(vals, data)
            if val is None:
                return None
            return str(val).lower()
        if op == "missing":
            # Accept a single key or list and return those absent from data
            keys = vals if isinstance(vals, list) else [vals]
            missing = []
            for k in keys:
                if _eval({"var": k}, data) is None:
                    missing.append(k)
            return missing
        if op == "var":
            if isinstance(vals, str):
                key, default = vals, None
            else:
                key, default = (vals + [None])[:2]
            cur = data
            for part in str(key).split("."):
                if isinstance(cur, dict):
                    cur = cur.get(part)
                else:
                    cur = None
                    break
            return default if cur is None else cur
        raise ValueError(f"Unsupported op {op}")
    if isinstance(node, list):
        return [_eval(v, data) for v in node]
    return node


def evaluate_rule(condition: dict, answers: dict) -> bool:
    """Evaluate a JSONLogic condition against provided answers."""
    return bool(_eval(condition, answers))
