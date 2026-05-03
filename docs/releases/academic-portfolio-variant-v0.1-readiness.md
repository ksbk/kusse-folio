# Release Readiness Report — Academic Portfolio Variant v0.1

Date: 2026-05-03

## Build Identification

- Branch: `feat/academic-portfolio-variant-v0.1`
- Commit (short): `3b73156`
- Commit (full): `3b73156db62c5f85d047169cc1827d82c974e200`

## Verification Results

### Preflight command

- Command: `make preflight`
- Result: **PASS**
- Environment: `.env` present with real `SECRET_KEY`; loaded automatically by `environ.Env.read_env()` in `config/settings/base.py`

### Full check matrix

- `uv run pytest -q`: PASS (`395 passed, 13 deselected`)
- `uv run ruff check .`: PASS
- `uv run mypy .`: PASS (`no issues found in 172 source files`)
- `uv run python manage.py check`: PASS (`no issues, 0 silenced`)
- `uv run python manage.py makemigrations --check --dry-run`: PASS (`No changes detected`)

## Known Limitations

- Local preflight depends on a valid `.env` file that sets `SECRET_KEY`.
- `make smoke` under `DEBUG=True` will fail the branded 404 check. Django replaces custom 404 templates with its own debug page when `DEBUG=True`. This is expected local-dev behaviour, not a code defect. Full branded 404 validation requires `DEBUG=False` and must be confirmed via `DEPLOY_URL=https://... make smoke-prod` against a deployed instance.

## Staging Smoke Test

- Status: **PENDING** — no staging deployment exists for this variant branch yet
- Smoke-test command: `DEPLOY_URL=https://<railway-domain> make smoke-prod`
- Required env vars before deploy (Railway project settings):
  - `SECRET_KEY` — generate with `uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
  - `DJANGO_SETTINGS_MODULE=config.settings.prod`
  - `ALLOWED_HOSTS=<railway-domain>`
  - `CSRF_TRUSTED_ORIGINS=https://<railway-domain>`
  - `DATABASE_URL` — from Railway Postgres plugin
  - `EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend` (staging)
  - `CONTACT_EMAIL=<monitored inbox>`
- Deploy command: `railway up --detach` from branch `feat/academic-portfolio-variant-v0.1`
- Next action: deploy to Railway, run `make smoke-prod`, record result here

## Decision

- **Conditionally ready for client/service delivery**: `make preflight` passes when `.env` exists with a real `SECRET_KEY`. No code changes to application behavior were required. The env loading architecture (Option A) was already correct.
- Upgrade to **full GO** after staging smoke test passes.
