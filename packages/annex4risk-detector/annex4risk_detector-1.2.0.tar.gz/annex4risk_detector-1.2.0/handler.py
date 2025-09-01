import json
import os

from risk_detector.dialog_orchestrator import DialogOrchestrator

DB_URL = os.environ["DB_URL"]
ORCH = DialogOrchestrator(DB_URL)


def start_session(customer_id: str | None = None) -> dict:
    session_id = ORCH.start_session(customer_id)
    return {"session_id": session_id}


def next_question(session_id: str) -> dict:
    return ORCH.next_question(session_id)


def submit_answer(session_id: str, feature_key: str, value) -> dict:
    ORCH.submit_answer(session_id, feature_key, value)
    return ORCH.next_question(session_id)


def lambda_handler(event: dict, context=None) -> dict:
    method = event.get("httpMethod")
    path = event.get("path")
    body = event.get("body")
    if body and isinstance(body, str):
        data = json.loads(body)
    elif isinstance(body, dict):
        data = body
    else:
        data = {}
    qs = event.get("queryStringParameters") or {}

    try:
        if path == "/session" and method == "POST":
            response = start_session(data.get("customer_id"))
        elif path == "/question" and method in {"GET", "POST"}:
            session_id = data.get("session_id") or qs.get("session_id")
            response = next_question(session_id)
        elif path == "/answer" and method == "POST":
            session_id = data["session_id"]
            feature_key = data["feature_key"]
            value = data["value"]
            response = submit_answer(session_id, feature_key, value)
        else:
            return {"statusCode": 404, "body": json.dumps({"error": "Not found"})}
    except KeyError as e:
        return {"statusCode": 400, "body": json.dumps({"error": f"Missing {e.args[0]}"})}

    return {"statusCode": 200, "body": json.dumps(response)}
