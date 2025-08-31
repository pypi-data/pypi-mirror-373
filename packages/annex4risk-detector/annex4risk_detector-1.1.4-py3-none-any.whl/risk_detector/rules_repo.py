"""Repository for loading rules, features and questions from DB."""
from sqlalchemy.orm import Session
from . import models

class RulesRepo:
    def __init__(self, db: Session):
        self.db = db

    def load(self):
        rules = self.db.query(models.RiskRule).all()
        feats = {f.key: f for f in self.db.query(models.RiskFeature).all()}
        qs = self.db.query(models.RiskQuestion).order_by(models.RiskQuestion.priority).all()
        version = rules[0].version if rules else "unknown"
        return rules, feats, qs, version
