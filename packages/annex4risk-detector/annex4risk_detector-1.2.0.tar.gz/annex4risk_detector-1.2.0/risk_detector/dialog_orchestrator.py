"""Simple dialog orchestrator for CLI demo with AI-generated questionnaires."""
from __future__ import annotations

import uuid
import os
from collections import Counter
from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from . import models
from .evaluators.jsonlogic_eval import evaluate_rule
from .classifiers.aggregator import classify
from .auto_rules import build_annex3_index, build_article5_index
from sqlalchemy import text as sql_text

PRIORITY = ["prohibited", "high_risk", "limited_risk", "minimal_risk"]

# Dynamic risk classification based on database features
def classify_from_answers(answers: dict) -> dict:
    """Classify risk dynamically based on database features and answers."""
    if not answers:
        return {"category": "minimal_risk", "score": 0.0, "legal_refs": [], "exception_applied": False}
    
    # If no database URL provided, use default
    db_url = os.getenv('ANNEX4AC_DB_URL') or os.getenv('DB_URL') or "sqlite:///risk.db"
    
    # Create database connection
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_recycle=3600, pool_size=5)
    
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as db:
            # ——— Legally correct, data-driven classifier (AI Act) ———
            features = {f.key: f for f in db.execute(select(models.RiskFeature)).scalars()}
            questions = {q.feature_key: q for q in db.execute(select(models.RiskQuestion)).scalars()}
            annex3 = build_annex3_index(db, table_name=os.environ.get("ANNEX_TABLE","rules"))
            all_items = {code for items in annex3["items"].values() for code,_ in items}
            art5   = build_article5_index(db, table_name=os.environ.get("ANNEX_TABLE","rules"))
            art5_codes = set(art5.get("items", {}).keys())

            legal_refs: list[str] = []
            exception_applied = False
            risk_factors: list[str] = []
            obligations: set[str] = set()

            def _truthy(v):
                if isinstance(v, bool): return v
                if v is None: return False
                if isinstance(v, (list, dict, tuple, set)): return len(v) > 0
                if isinstance(v, str): return v.strip() != ""
                return True

            # Collect obligations from answered questions' legal_bases
            for fk, v in answers.items():
                if not _truthy(v):
                    continue
                q = questions.get(fk)
                if q and getattr(q, "legal_bases", None):
                    obligations.update(q.legal_bases or [])

            # Article 5 → prohibited
            if any((lb in art5_codes or str(lb).startswith("Article 5")) for lb in obligations):
                return {
                    "category": "prohibited",
                    "score": 1.0,
                    "legal_refs": ["Article 5"],
                    "exception_applied": False,
                    "risk_factors": ["article5"],
                    "obligations": sorted(obligations),
                }

            # Annex III item selected → high-risk (Art. 6(2)), unless Article 6(3) applies
            annex3_item = answers.get("annex3_item")
            if isinstance(annex3_item, str) and annex3_item in all_items:
                category = "high_risk"
                legal_refs.append(annex3_item)
                risk_factors.append(f"annex3:{annex3_item}")

                a63 = answers.get("a6_conditions") or []
                if isinstance(a63, list) and len(a63) > 0:
                    category = "limited_risk"
                    exception_applied = True
                    legal_refs.append("Article 6(3)")

                return {
                    "category": category,
                    "score": 1.0 if category == "high_risk" else 0.5,
                    "legal_refs": sorted(set(legal_refs)),
                    "exception_applied": exception_applied,
                    "risk_factors": risk_factors,
                    "obligations": sorted(obligations),
                }

            # No Annex III / Article 5 triggers → minimal
            return {
                "category": "minimal_risk",
                "score": 0.0,
                "legal_refs": [],
                "exception_applied": False,
                "risk_factors": [],
                "obligations": sorted(obligations),
            }
            
    except Exception as e:
        # Fallback to minimal risk if database access fails
        return {
            "category": "minimal_risk", 
            "score": 0.0, 
            "legal_refs": [], 
            "exception_applied": False,
            "error": f"Database error: {str(e)}"
        }


class DialogOrchestrator:
    def __init__(self, db_url: str):
        if db_url.startswith("sqlite"):
            self.engine = create_engine(db_url, connect_args={"check_same_thread": False})
        else:
            self.engine = create_engine(db_url, pool_recycle=3600, pool_size=5)
        self.Session = sessionmaker(bind=self.engine)

    def start_session(self, customer_id: str = None) -> str:
        with self.Session() as db:
            # Get current questionnaire version from meta_kv
            version_result = db.execute(sql_text("SELECT value FROM meta_kv WHERE key='annex3_hash'")).scalar()
            version = version_result or "unknown"
            
            session_id = str(uuid.uuid4())
            chat = models.ChatSession(
                id=session_id, customer_id=customer_id, rule_snapshot_version=version
            )
            db.add(chat)
            db.commit()
            return session_id

    def _get_missing_required_features(self, features, questions, answers):
        """
        Return required features that are currently *visible* under gating and still unanswered.
        This prevents blocking on required fields that are not yet gated-in.
        """
        missing: list[str] = []
        for q in sorted(questions, key=lambda q: getattr(q, "priority", 0)):
            f = features.get(q.feature_key)
            if not f:
                continue
            if q.feature_key in answers:
                continue
            if q.gating and not evaluate_rule(q.gating, answers):
                continue
            if getattr(f, "required", False):
                missing.append(q.feature_key)
        return missing

    def _visible_unanswered(self, questions, answers):
        """List feature_keys for questions that are currently visible (gating passes) and unanswered."""
        out = []
        for q in questions:
            if q.feature_key in answers:
                continue
            if q.gating and not evaluate_rule(q.gating, answers):
                continue
            out.append(q.feature_key)
        return out

    def _get_next_question(self, questions, features, answers):
        """Get the next question to ask based on priority and gating."""
        for q in sorted(questions, key=lambda q: getattr(q, "priority", 0)):
            if q.feature_key in answers:
                continue
            if q.gating and not evaluate_rule(q.gating, answers):
                continue
            
            f = features.get(q.feature_key)
            if not f:
                continue
                
            result = {
                "feature_key": q.feature_key,
                "prompt": q.prompt_en or f.prompt_en,
                "type": f.type,
                "options": f.options,
            }
            
            # Dynamic filtering for annex3_item based on selected area
            if q.feature_key == "annex3_item":
                area = answers.get("annex3_area")
                if area:
                    # Filter options to only show items under the selected area
                    filtered_options = [opt for opt in f.options if opt.startswith(area + ".")]
                    if filtered_options:
                        result["options"] = filtered_options
                    else:
                        result["options"] = [area]  # Fallback to area itself
            
            return result
        return None

    def next_question(self, session_id: str):
        with self.Session() as db:
            chat = db.get(models.ChatSession, session_id)
            if not chat:
                raise RuntimeError(f"Chat session not found: {session_id}")
            
            # Load AI-generated features and questions
            features = {f.key: f for f in db.execute(select(models.RiskFeature)).scalars()}
            questions = list(db.execute(select(models.RiskQuestion).order_by(models.RiskQuestion.priority)).scalars())
            answers = {a.feature_key: a.value for a in chat.answers}
            
            # Get current questionnaire version
            version_result = db.execute(sql_text("SELECT value FROM meta_kv WHERE key='annex3_hash'")).scalar()
            version = version_result or "unknown"

            def finalize():
                """Finalize the session with risk classification."""
                outcome = classify_from_answers(answers)
                reasoning = {"outcome": outcome, "answers": answers}
                res = models.RiskOutcome(
                    id=str(uuid.uuid4()),
                    session_id=session_id,
                    rule_snapshot_version=version,
                    category=outcome["category"],
                    score=outcome["score"],
                    reasoning=reasoning,
                    legal_refs=outcome["legal_refs"],
                    exception_applied=outcome["exception_applied"],
                )
                db.add(res)
                db.commit()
                return {"outcome": outcome, "answers": answers}

            # Fast-path: if Article 5 was selected, finish immediately.
            # (Classifier will return "prohibited" based on legal_bases from that question.)
            if answers.get("prohibited_item"):
                return finalize()

            # Generic early-finish rule:
            # if no gated question remains visible (i.e., nothing to ask now), finalize.
            visible_still_unanswered = self._visible_unanswered(questions, answers)
            if not visible_still_unanswered:
                return finalize()

            # Find next question to ask
            next_q = self._get_next_question(questions, features, answers)
            if next_q:
                return next_q

            # If no next question, check if any required (and *visible*) features remain; otherwise finalize
            missing = self._get_missing_required_features(features, questions, answers)
            if missing:
                raise RuntimeError(f"Missing required answers for: {', '.join(missing)}")

            return finalize()

    def submit_answer(self, session_id: str, feature_key: str, value):
        with self.Session() as db:
            if not db.get(models.ChatSession, session_id):
                raise RuntimeError(f"Chat session not found: {session_id}")
            ans = models.ChatAnswer(
                id=str(uuid.uuid4()),
                session_id=session_id,
                feature_key=feature_key,
                value=value,
            )
            db.add(ans)
            db.commit()
