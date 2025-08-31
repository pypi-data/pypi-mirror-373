import json
import importlib
from io import BytesIO
from unittest.mock import patch

import boto3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from risk_detector import models


class LocalLambdaClient:
    def __init__(self, func):
        self.func = func

    def invoke(self, FunctionName, Payload):
        if isinstance(Payload, (bytes, bytearray)):
            event = json.loads(Payload.decode())
        else:
            event = json.loads(Payload.read())
        res = self.func(event, None)
        return {
            "StatusCode": res.get("statusCode", 200),
            "Payload": BytesIO(json.dumps(res).encode()),
        }


def test_lambda_api_flow(synced_rules, monkeypatch):
    db_url, _ = synced_rules
    monkeypatch.setenv("DB_URL", db_url)
    handler = importlib.import_module("handler")
    importlib.reload(handler)

    fake_client = LocalLambdaClient(handler.lambda_handler)
    with patch("boto3.client", lambda service, **kwargs: fake_client):
        client = boto3.client("lambda", region_name="us-east-1")

        payload = json.dumps({"httpMethod": "POST", "path": "/session", "body": "{}"}).encode()
        resp = client.invoke(FunctionName="risk-detector", Payload=payload)
        result = json.loads(resp["Payload"].read())
        assert result["statusCode"] == 200
        session_id = json.loads(result["body"])["session_id"]
        assert session_id

        engine = create_engine(db_url)
        Session = sessionmaker(bind=engine)
        db = Session()

        plan = {
            "domain": "other",
            "automation_level": "human_controlled",
            "consequence_level": "low",
            "is_chat_interface": False,
            "specific_usecases": [],
        }

        answers = 0
        while True:
            payload = json.dumps(
                {
                    "httpMethod": "GET",
                    "path": "/question",
                    "queryStringParameters": {"session_id": session_id},
                    "body": None,
                }
            ).encode()
            resp = client.invoke(FunctionName="risk-detector", Payload=payload)
            res = json.loads(resp["Payload"].read())
            body = json.loads(res["body"])
            if "outcome" in body:
                outcome = body["outcome"]
                break

            fk = body["feature_key"]
            t = body["type"]
            value = plan.get(
                fk,
                False if t == "boolean" else ([] if t == "multiselect" else ""),
            )
            payload = json.dumps(
                {
                    "httpMethod": "POST",
                    "path": "/answer",
                    "body": json.dumps(
                        {"session_id": session_id, "feature_key": fk, "value": value}
                    ),
                }
            ).encode()
            client.invoke(FunctionName="risk-detector", Payload=payload)
            answers += 1
            stored = (
                db.query(models.ChatAnswer)
                .filter_by(session_id=session_id, feature_key=fk)
                .first()
            )
            assert stored is not None
            assert stored.value == value

        assert outcome["category"] == "minimal_risk"
        assert db.query(models.ChatAnswer).filter_by(session_id=session_id).count() == answers
        db.close()
