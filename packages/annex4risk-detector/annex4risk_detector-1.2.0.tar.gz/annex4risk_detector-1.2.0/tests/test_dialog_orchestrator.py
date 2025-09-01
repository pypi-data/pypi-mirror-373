import pytest
from unittest.mock import MagicMock

from risk_detector import dialog_orchestrator
from risk_detector.dialog_orchestrator import DialogOrchestrator


class DummyChat:
    def __init__(self):
        self.answers = []


class DummySession:
    def __init__(self, commit_raises: Exception | None = None):
        self.closed = False
        self.commit_raises = commit_raises

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        self.closed = True

    def add(self, obj):
        pass

    def commit(self):
        if self.commit_raises:
            raise self.commit_raises

    def get(self, model, id):
        return DummyChat()


def orchestrator_with_session(monkeypatch, session: DummySession, repo: MagicMock | None = None):
    orch = DialogOrchestrator("sqlite://")
    orch.Session = lambda: session
    if repo is not None:
        monkeypatch.setattr(dialog_orchestrator, "RulesRepo", lambda db: repo)
    return orch


def default_repo():
    repo = MagicMock()
    repo.load.return_value = ([], {}, [], "v1")
    return repo


def test_start_session_closes_session(monkeypatch):
    session = DummySession()
    repo = default_repo()
    orch = orchestrator_with_session(monkeypatch, session, repo)
    orch.start_session()
    assert session.closed


def test_start_session_closes_session_on_exception(monkeypatch):
    session = DummySession()
    repo = MagicMock()
    repo.load.side_effect = RuntimeError("boom")
    orch = orchestrator_with_session(monkeypatch, session, repo)
    with pytest.raises(RuntimeError):
        orch.start_session()
    assert session.closed


def test_submit_answer_closes_session():
    session = DummySession()
    orch = DialogOrchestrator("sqlite://")
    orch.Session = lambda: session
    orch.submit_answer("sid", "fk", "val")
    assert session.closed


def test_submit_answer_closes_session_on_exception():
    session = DummySession(commit_raises=RuntimeError("boom"))
    orch = DialogOrchestrator("sqlite://")
    orch.Session = lambda: session
    with pytest.raises(RuntimeError):
        orch.submit_answer("sid", "fk", "val")
    assert session.closed


def test_submit_answer_raises_when_chat_missing():
    session = DummySession()
    session.get = lambda model, id: None
    orch = DialogOrchestrator("sqlite://")
    orch.Session = lambda: session
    with pytest.raises(RuntimeError, match="Chat session not found"):
        orch.submit_answer("sid", "fk", "val")
    assert session.closed


def test_next_question_closes_session(monkeypatch):
    session = DummySession()
    repo = default_repo()
    orch = orchestrator_with_session(monkeypatch, session, repo)
    orch.next_question("sid")
    assert session.closed


def test_next_question_closes_session_on_exception(monkeypatch):
    session = DummySession()
    repo = MagicMock()
    repo.load.side_effect = RuntimeError("boom")
    orch = orchestrator_with_session(monkeypatch, session, repo)
    with pytest.raises(RuntimeError):
        orch.next_question("sid")
    assert session.closed


def test_next_question_raises_when_chat_missing(monkeypatch):
    session = DummySession()
    session.get = lambda model, id: None
    repo = default_repo()
    orch = orchestrator_with_session(monkeypatch, session, repo)
    with pytest.raises(RuntimeError, match="Chat session not found"):
        orch.next_question("sid")
    assert session.closed


def test_next_question_uses_lowest_priority_for_missing(monkeypatch):
    session = DummySession()
    feature_a = MagicMock(prompt_en="A", type="str", options=None, required=True)
    feature_b = MagicMock(prompt_en="B", type="str", options=None, required=True)
    q1 = MagicMock(feature_key="a", gating=None, priority=10, prompt_en=None)
    q2 = MagicMock(feature_key="b", gating=None, priority=5, prompt_en=None)
    repo = MagicMock()
    repo.load.return_value = ([], {"a": feature_a, "b": feature_b}, [q1, q2], "v1")
    monkeypatch.setattr(
        dialog_orchestrator,
        "build_questions",
        lambda rules, feats, qs, answers: [],
    )
    orch = orchestrator_with_session(monkeypatch, session, repo)
    res = orch.next_question("sid")
    assert res["feature_key"] == "b"
    assert session.closed
