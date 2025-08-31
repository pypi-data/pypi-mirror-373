from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from risk_detector.rules_repo import RulesRepo
from risk_detector import models

def test_sync_rules_and_repo_load(synced_rules):
    db_url, rules_dir = synced_rules
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()

    # в БД есть фичи/правила/вопросы
    assert db.query(models.RiskFeature).count() > 0
    assert db.query(models.RiskRule).count() > 0
    assert db.query(models.RiskQuestion).count() > 0

    repo = RulesRepo(db)
    rules, feats, qs, version = repo.load()

    # features — dict по key, rules и qs — списки ORM-объектов
    assert "domain" in feats and hasattr(feats["domain"], "type")
    assert any(r.category in {"prohibited", "high_risk","limited_risk","minimal_risk"} for r in rules)
    assert any(q.feature_key == "domain" for q in qs)
    assert isinstance(version, str)
