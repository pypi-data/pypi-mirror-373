from __future__ import annotations

import os
import json
import subprocess
import sys
import hashlib

from sqlalchemy import create_engine, text, text as sql_text


def _get_engine(db_url: str):
    if db_url.startswith("sqlite"):
        return create_engine(db_url, connect_args={"check_same_thread": False})
    return create_engine(db_url, pool_recycle=3600, pool_size=5)


def ensure_kv(engine):
    with engine.begin() as cx:
        cx.execute(
            text(
                """
            CREATE TABLE IF NOT EXISTS kv (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
            )
        )


def kv_get(engine, key: str) -> str | None:
    with engine.begin() as cx:
        r = cx.execute(text("SELECT value FROM kv WHERE key=:k"), {"k": key}).fetchone()
        return r[0] if r else None


def kv_set(engine, key: str, value: str):
    with engine.begin() as cx:
        cx.execute(
            text(
                """
            INSERT INTO kv(key, value) VALUES(:k, :v)
            ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
            """
            ),
            {"k": key, "v": value},
        )


def current_annex3_hash(engine, table: str | None = None) -> str | None:
    """Compute hash directly from DB without invoking the LLM."""
    table = table or os.environ.get("ANNEX_TABLE", "rules")
    with engine.begin() as cx:
        rows = cx.execute(
            sql_text(
                """
            SELECT section_code, COALESCE(title,''), COALESCE(content,'')
            FROM {table}
            WHERE section_code LIKE 'AnnexIII%'
            ORDER BY section_code
        """.format(table=table)
            )
        ).fetchall()
    areas, items = {}, {}
    for sc, title, content in rows:
        if sc.count('.') == 1:
            label = (title or content.split(':', 1)[0] or sc).strip()
            areas[sc] = label
            items[sc] = []
        elif sc.count('.') == 2:
            parent = sc.rsplit('.', 1)[0]
            raw = content or title or sc
            short = raw.strip().split('\n', 1)[0].strip().rstrip('.;')
            items.setdefault(parent, []).append((sc, short))
    for area_code, label in areas.items():
        if not items.get(area_code):
            items[area_code] = [(area_code, label)]
    m = hashlib.sha256()
    for k in sorted(areas.keys()):
        m.update(k.encode()); m.update(b"::"); m.update(areas[k].encode())
    for area in sorted(items.keys()):
        for code, label in sorted(items[area], key=lambda x: x[0]):
            m.update(area.encode()); m.update(b"::"); m.update(code.encode()); m.update(b"::"); m.update(label.encode())
    return m.hexdigest()


def run():
    db_url = os.environ["DB_URL"]
    engine = _get_engine(db_url)
    ensure_kv(engine)
    last_hash = kv_get(engine, "annex3_hash")
    new_hash = current_annex3_hash(engine)
    if not new_hash:
        print("WARN: cannot compute annex3_hash; skip")
        return
    if new_hash == last_hash:
        print("No changes in Annex III; nothing to do.")
        return
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    subprocess.check_call([sys.executable, "ai_question_gen_llm.py", "--db-url", db_url, "--model", model])
    kv_set(engine, "annex3_hash", new_hash)
    print("Questions regenerated and hash updated.")


if __name__ == "__main__":
    run()

