import json
import importlib


def test_handler_flow_minimal_risk(synced_rules, monkeypatch):
    db_url, _ = synced_rules
    monkeypatch.setenv("DB_URL", db_url)
    handler = importlib.import_module("handler")
    importlib.reload(handler)

    # Start session
    res = handler.lambda_handler({"httpMethod": "POST", "path": "/session", "body": "{}"})
    assert res["statusCode"] == 200
    session_id = json.loads(res["body"])["session_id"]

    plan = {
        "domain": "other",
        "automation_level": "human_controlled",
        "consequence_level": "low",
    }

    while True:
        # Get next question
        res = handler.lambda_handler({
            "httpMethod": "GET",
            "path": "/question",
            "queryStringParameters": {"session_id": session_id},
            "body": None,
        })
        body = json.loads(res["body"])
        if "outcome" in body:
            outcome = body["outcome"]
            break
        fk = body["feature_key"]
        t = body["type"]
        value = plan.get(fk, False if t == "boolean" else ([] if t == "multiselect" else ""))
        # Submit answer and get next question/outcome
        res = handler.lambda_handler({
            "httpMethod": "POST",
            "path": "/answer",
            "body": json.dumps({
                "session_id": session_id,
                "feature_key": fk,
                "value": value,
            }),
        })
        body = json.loads(res["body"])
        if "outcome" in body:
            outcome = body["outcome"]
            break

    assert outcome["category"] == "minimal_risk"
