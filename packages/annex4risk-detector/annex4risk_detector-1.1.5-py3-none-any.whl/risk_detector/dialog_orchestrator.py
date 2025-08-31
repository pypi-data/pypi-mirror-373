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
from sqlalchemy import text as sql_text

PRIORITY = ["prohibited", "high_risk", "limited_risk", "minimal_risk"]

# Dynamic risk classification based on database features
def classify_from_answers(answers: dict) -> dict:
    """Classify risk dynamically based on database features and answers."""
    if not answers:
        return {"category": "minimal_risk", "score": 0.0, "legal_refs": [], "exception_applied": False}
    
    # If no database URL provided, use default
    db_url = os.getenv('DB_URL')
    
    # Create database connection
    if db_url.startswith("sqlite"):
        engine = create_engine(db_url, connect_args={"check_same_thread": False})
    else:
        engine = create_engine(db_url, pool_recycle=3600, pool_size=5)
    
    Session = sessionmaker(bind=engine)
    
    try:
        with Session() as db:
            # Load all features from database
            features = {f.key: f for f in db.execute(select(models.RiskFeature)).scalars()}
            questions = {q.feature_key: q for q in db.execute(select(models.RiskQuestion)).scalars()}
            
            # Calculate dynamic risk score
            total_risk_score = 0.0
            risk_factors = []
            legal_refs = []
            exception_applied = False
            
            # Process each answer against database features
            for feature_key, value in answers.items():
                feature = features.get(feature_key)
                if not feature:
                    continue
                
                question = questions.get(feature_key)
                priority_weight = (question.priority / 100.0) if question and question.priority else 0.5
                
                # Calculate risk contribution based on feature type
                risk_contribution = 0.0
                
                if feature.type == "boolean":
                    if value is True:
                        # Boolean True contributes risk based on priority
                        risk_contribution = priority_weight * 0.3
                        risk_factors.append(f"{feature_key}: {feature.prompt_en or 'Yes'}")
                
                elif feature.type == "enum" and feature.options:
                    options = feature.options if isinstance(feature.options, list) else []
                    if value in options:
                        # Enum risk based on position in options (later = higher risk) and priority
                        option_index = options.index(value)
                        option_risk = (option_index + 1) / len(options)  # 0.x to 1.0
                        risk_contribution = priority_weight * option_risk * 0.4
                        risk_factors.append(f"{feature_key}: {value}")
                
                elif feature.type == "array" and isinstance(value, list):
                    if len(value) > 0:
                        # Array risk based on number of items and priority
                        array_risk = min(len(value) / 5.0, 1.0)  # Cap at 1.0
                        risk_contribution = priority_weight * array_risk * 0.3
                        risk_factors.append(f"{feature_key}: {len(value)} items")
                
                total_risk_score += risk_contribution
                
                # Add to legal references if significant contribution
                if risk_contribution > 0.1:
                    legal_refs.append(feature_key)
            
            # Normalize and categorize risk
            normalized_score = min(total_risk_score, 1.0)
            
            if normalized_score < 0.2:
                category = "minimal_risk"
            elif normalized_score < 0.5:
                category = "limited_risk"
            elif normalized_score < 0.8:
                category = "high_risk"
            else:
                category = "unacceptable_risk"
            
            return {
                "category": category,
                "score": round(normalized_score, 2),
                "legal_refs": legal_refs,
                "exception_applied": exception_applied,
                "risk_factors": risk_factors[:5]  # Limit to top 5 factors
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

    def _get_missing_required_features(self, features, answers):
        """Get list of required features that are missing answers."""
        missing = []
        for f in features.values():
            if getattr(f, "required", False) and f.key not in answers:
                missing.append(f.key)
        return missing

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

            # Check if we can make a classification decision early
            # If we have annex3_item and all relevant carve-out questions are answered
            annex3_item = answers.get("annex3_item")
            if annex3_item:
                # Check if we have enough information for classification
                required_for_item = []
                
                # Check which carve-out questions are relevant for this item
                if annex3_item == "AnnexIII.1.a":
                    required_for_item.append("exclusion_biometric_verification_only")
                elif annex3_item == "AnnexIII.5.b":
                    required_for_item.append("exclusion_credit_fraud_detection_only")
                elif annex3_item == "AnnexIII.8.b":
                    required_for_item.append("campaign_outputs_direct_to_voters")
                elif annex3_item == "AnnexIII.6.d":
                    required_for_item.append("solely_based_on_profiling")
                
                # Check if all required carve-outs are answered
                all_answered = all(req in answers for req in required_for_item)
                
                # If we have a6_conditions or all carve-outs answered, we can classify
                if "a6_conditions" in answers or all_answered:
                    return finalize()

            # Find next question to ask
            next_q = self._get_next_question(questions, features, answers)
            if next_q:
                return next_q

            # If no more questions and we have basic info, finalize
            if annex3_item:
                return finalize()
            
            # Check for missing required features
            missing = self._get_missing_required_features(features, answers)
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
