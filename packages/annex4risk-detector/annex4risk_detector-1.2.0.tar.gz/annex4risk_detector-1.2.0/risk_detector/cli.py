"""Command line interface for risk detector."""
import json
import uuid
import hashlib
from datetime import datetime
from pathlib import Path

import click
import yaml
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from . import models
from .coverage import check_coverage
from .dialog_orchestrator import DialogOrchestrator


class CommaSeparatedChoice(click.ParamType):
    """Click param type parsing comma-separated choices."""

    name = "comma_separated_choice"

    def __init__(self, choices):
        self.choices = choices

    def convert(self, value, param, ctx):
        items = [v.strip() for v in value.split(",") if v.strip()]
        invalid = [v for v in items if v not in self.choices]
        if invalid:
            self.fail(
                f"invalid choice(s): {', '.join(invalid)}. Choose from {', '.join(self.choices)}",
                param,
                ctx,
            )
        return items

@click.group()
def cli():
    """Risk detector utilities."""


@cli.command(name="init_db")
@click.option("--db-url", required=True)
def init_db(db_url):
    """Initialise database tables."""
    engine = create_engine(db_url)
    models.Base.metadata.create_all(engine)
    click.echo("DB initialised")


@cli.command(name="sync_rules")
@click.option("--db-url", required=True)
@click.option(
    "--dir",
    "rules_dir",
    type=click.Path(exists=True),
    help="Directory with YAML rule files; defaults to packaged rules",
)
def sync_rules(db_url, rules_dir):
    """Load features, rules and questions from YAML into DB."""
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    session = Session()
    if rules_dir:
        base = Path(rules_dir)
    else:
        from importlib import resources

        base = resources.files("risk_detector") / "rules" / "risk"
    required = ["features.yaml", "rules.yaml", "questions.yaml"]
    missing = [name for name in required if not (base / name).is_file()]
    if missing:
        raise click.ClickException(
            "Missing required file(s): " + ", ".join(missing)
        )

    feat_text = (base / "features.yaml").read_text()
    rule_text = (base / "rules.yaml").read_text()
    q_text = (base / "questions.yaml").read_text()
    features = yaml.safe_load(feat_text) or []
    rules = yaml.safe_load(rule_text) or []
    questions = yaml.safe_load(q_text) or []
    sha = hashlib.sha256()
    for part in (feat_text, rule_text, q_text):
        sha.update(part.encode("utf-8"))
    ruleset_version = sha.hexdigest()
    # Delete in dependency order to satisfy foreign key constraints
    session.query(models.RiskQuestion).delete()
    session.query(models.RiskFeature).delete()
    for f in features:
        session.add(models.RiskFeature(id=str(uuid.uuid4()), **f))
    for q in questions:
        q = dict(q)
        q_id = q.pop("id", str(uuid.uuid4()))
        session.add(models.RiskQuestion(id=q_id, **q))
    session.commit()
    click.echo(f"Rules synced (version {ruleset_version})")


@cli.command()
@click.option("--rules-dir", required=True, type=click.Path(exists=True))
def coverage(rules_dir):
    base = Path(rules_dir)
    missing, missing_q = check_coverage(
        base / "rules.yaml", base / "features.yaml", base / "questions.yaml"
    )
    if missing or missing_q:
        click.echo("Missing features: %s" % missing)
        click.echo("Missing questions: %s" % missing_q)
        raise SystemExit(1)
    click.echo("Coverage OK")


@cli.command()
@click.option("--db-url", required=True)
@click.option("--customer-id", default=None)
def chat(db_url, customer_id):
    """Run simple interactive chat in console."""
    orch = DialogOrchestrator(db_url)
    session_id = orch.start_session(customer_id)
    click.echo("Session %s" % session_id)
    while True:
        nxt = orch.next_question(session_id)
        if "outcome" in nxt:
            click.echo(json.dumps(nxt["outcome"], indent=2))
            break
        prompt = nxt["prompt"]
        ftype = nxt["type"]
        options = nxt.get("options") or []
        if ftype == "enum" and options:
            prompt += " (" + ", ".join(options) + ")"
            value = click.prompt(prompt, type=click.Choice(options))
        elif ftype == "multiselect" and options:
            prompt += " [comma-separated] (" + ", ".join(options) + ")"
            value = click.prompt(
                prompt, type=CommaSeparatedChoice(options), default="", show_default=False
            )
        elif ftype == "boolean":
            value = click.confirm(prompt, default=False)
        else:
            value = click.prompt(prompt, default="", show_default=False)
        orch.submit_answer(session_id, nxt["feature_key"], value)


@cli.command()
@click.option("--db-url", required=True)
@click.option("--session-id", required=True)
@click.option("--by", "signed_by", required=True)
def signoff(db_url, session_id, signed_by):
    """Mark the latest outcome of a session as signed off."""
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    out = (
        db.query(models.RiskOutcome)
        .filter_by(session_id=session_id)
        .order_by(models.RiskOutcome.created_at.desc())
        .first()
    )
    if not out:
        raise SystemExit("No outcome for this session")
    out.signed_off = True
    out.signed_off_by = signed_by
    out.signed_off_at = datetime.utcnow()
    db.commit()
    click.echo("Signed off")


@cli.command(name="export_json")
@click.option("--db-url", required=True)
@click.option("--session-id", required=True)
@click.option("--out", "out_path", required=True, type=click.Path())
def export_json(db_url, session_id, out_path):
    """Export latest outcome of a session to a JSON file."""
    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)
    db = Session()
    out = (
        db.query(models.RiskOutcome)
        .filter_by(session_id=session_id)
        .order_by(models.RiskOutcome.created_at.desc())
        .first()
    )
    if not out:
        raise SystemExit("No outcome for this session")
    Path(out_path).write_text(
        json.dumps(
            {
                "session_id": session_id,
                "rule_snapshot_version": out.rule_snapshot_version,
                "category": out.category,
                "score": out.score,
                "legal_refs": out.legal_refs,
                "reasoning": out.reasoning,
                "signed_off": out.signed_off,
                "signed_off_by": out.signed_off_by,
                "signed_off_at": out.signed_off_at.isoformat()
                if out.signed_off_at
                else None,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    click.echo(f"Saved {out_path}")

if __name__ == "__main__":
    cli()
