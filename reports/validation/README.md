# Validation Record

## Automated checks

Run:

```bash
python -m compileall app.py src tests scripts
python -m unittest discover -s tests -v
python scripts/check_secrets.py
python scripts/check_docs.py
ruff check app.py src tests scripts
ruff format --check app.py src tests scripts
```

## Required human checks

- Review all prototype wording for unsupported scientific or regulatory claims.
- Confirm every displayed finding references evidence or explicitly reports a gap.
- Exercise balanced, missing-evidence, ecological-constraint, and regulatory-restriction scenarios.
- Confirm no displayed status is described as approval, authorization, certification, or professional advice.
- Confirm reported Bob capabilities and workflow measurements match retained evidence.
