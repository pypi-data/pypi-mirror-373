# Risk Detector

Minimal skeleton of dynamic risk classification chat assistant.

## Installation

```bash
pip install -r requirements.txt
# or install the package
pip install .
```

## CLI usage

The project exposes a command line interface providing helpers to manage rules and run the interactive dialog.

```bash
annex4risk-detector --help
```

Typical workflow:

```bash
# create database tables
annex4risk-detector init_db --db-url sqlite:///risk.db

# load YAML rules into the database
annex4risk-detector sync_rules --db-url sqlite:///risk.db --dir path/to/rules

# start an interactive classification chat
annex4risk-detector chat --db-url sqlite:///risk.db
```

See `risk-detector --help` for all available commands.

## Demo script

For a quick demonstration with a temporary SQLite database and pre-filled
answers that exercise all risk levels, run:

```bash
python demo_script.py
```

The script loads sample rules from `test_rules/risk` and shows how the dialog
flows for four scenarios ending in the `prohibited`, `high_risk`,
`limited_risk`, and `minimal_risk` categories.

## Serverless deployment

When deploying the Lambda handler, use a database reachable from the
serverless environment (for example, an Amazon RDS PostgreSQL instance).
Expose the connection string via the `DB_URL` environment variable –
`handler.py` reads this variable and passes it to `DialogOrchestrator`.

Before deployment initialise the database and load the rules:

```bash
annex4risk-detector init_db --db-url "$DB_URL"
annex4risk-detector sync_rules --db-url "$DB_URL" --dir path/to/rules
```

These commands create tables including `chat_answers` and `risk_outcomes`
which persist every answer and classification result.
