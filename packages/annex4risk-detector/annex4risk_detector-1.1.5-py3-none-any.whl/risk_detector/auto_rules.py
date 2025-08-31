from __future__ import annotations

import hashlib
import re
from typing import Any, Dict

from sqlalchemy import text as sql_text

_WS = re.compile(r"\s+")

def _norm_space(s: str | None) -> str:
    return _WS.sub(" ", (s or "").strip())

def _firstline(s: str | None) -> str:
    s = (s or "").strip()
    return s.splitlines()[0].strip() if s else ""

def build_annex3_index(db, table_name: str = "rules") -> Dict[str, Any]:
    """
    Читает ТОЛЬКО таблицу `rules` и строит индекс Annex III:
      - areas: { "AnnexIII.1": "Label", ..., "AnnexIII.8": "Label" }
      - items: { "AnnexIII.1": [("AnnexIII.1.a","Short"), ...], ... }
      - content: { "AnnexIII.1.a": "<title>\\n<content>", ... }
    Любые строки без подпунктов автоматически считаются "item" самого area.
    """
    rows = db.execute(sql_text(f"""
        SELECT section_code,
               COALESCE(title,'')   AS title,
               COALESCE(content,'') AS content
        FROM {table_name}
        WHERE section_code LIKE 'AnnexIII%%'
        ORDER BY section_code
    """)).fetchall()

    areas: Dict[str, str] = {}
    items: Dict[str, list[tuple[str, str]]] = {}
    content_map: Dict[str, str] = {}

    for sc, title, content in rows:
        content_map[sc] = (title or "") + ("\n" if title and content else "") + (content or "")
        if sc.count(".") == 1:
            label = _norm_space(title) or _firstline(content) or sc
            areas[sc] = label
            items.setdefault(sc, [])
        elif sc.count(".") == 2:
            parent = sc.rsplit(".", 1)[0]
            raw = title or content or sc
            short = _firstline(raw).rstrip(".;")
            items.setdefault(parent, []).append((sc, short))

    # Если у области нет подпунктов — сделаем саму область её item'ом
    for area_code, label in list(areas.items()):
        if not items.get(area_code):
            items[area_code] = [(area_code, label)]

    # Стабильная сортировка подпунктов по коду
    for area_code in list(items.keys()):
        items[area_code] = sorted(items[area_code], key=lambda x: x[0])

    return {"areas": areas, "items": items, "content": content_map}

def annex3_hash(annex3_index: Dict[str, Any]) -> str:
    """
    Хэш только из КОДОВ и меток Annex III, чтобы любое изменение в `rules`
    гарантированно меняло хэш и триггерило регенерацию.
    """
    m = hashlib.sha256()
    for area_code in sorted(annex3_index["areas"].keys()):
        m.update(area_code.encode()); m.update(b"::")
        m.update(_norm_space(annex3_index["areas"][area_code]).encode())
    for area_code in sorted(annex3_index["items"].keys()):
        for code, label in annex3_index["items"][area_code]:
            m.update(area_code.encode()); m.update(b"::")
            m.update(code.encode()); m.update(b"::")
            m.update(_norm_space(label).encode())
    return m.hexdigest()
