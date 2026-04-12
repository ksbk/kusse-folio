# Testing

This file defines testing policy and execution rules. It does not list individual UI states. State-by-state coverage lives in [TEST_MATRIX.md](TEST_MATRIX.md).

## Principles

- Test the lowest layer that can prove the behavior reliably.
- Use browser tests for keyboard flow, focus management, scroll lock, and responsive navigation behavior.
- Use view/model/template tests for render-path selection, context values, and config-driven DOM changes.
- Use repeatable visual audit scripts for contrast, responsive fit, and layout states that are not practical to assert in unit tests.
- Keep coverage gaps explicit in `TEST_MATRIX.md`; do not imply coverage that does not exist.

## Current Test Layers

| Layer | Purpose | Current entrypoints |
| --- | --- | --- |
| Unit / model | Field defaults, validation, helper functions, and singleton behavior | `tests/site/test_models.py`, `tests/core/test_templatetags.py`, `tests/contact/test_forms.py`, `tests/projects/test_models.py` |
| View / template | Context values and DOM path selection without a browser | `tests/pages/test_views.py`, `tests/services/test_views.py`, `tests/projects/test_views.py`, `tests/contact/test_views.py` |
| Admin safety | Singleton guards and admin warning behavior | `tests/site/test_admin.py`, `tests/projects/test_admin.py`, `tests/contact/test_admin.py` |
| Browser e2e | Navigation, user journeys, and JS behavior | `tests/e2e/` |
| Content readiness | Buyer pre-launch auditing against starter/default content in the deployment database | `apps/site/management/commands/check_content_readiness.py`, `tests/site/test_management_commands.py` |
| Deploy / system | Django checks, migration drift, deploy checks, requirements sync | `make health`, `make check-deploy`, `make check-reqs`, `.github/workflows/ci.yml` |
| Smoke / live instance | Post-deploy URL verification | `scripts/smoke_check.py`, `make smoke`, `make smoke-prod` |
| Visual audit | Screenshot capture and pixel-level heuristics for broad page review | `scripts/take_screenshots.py`, `scripts/analyse_screenshots.py`, `artifacts/visual-audit/` |

## Standard Commands

| Goal | Command |
| --- | --- |
| Full repo gate | `make health` |
| Unit + view tests only | `uv run pytest` |
| Browser e2e | `make test-e2e` |
| Coverage report | `uv run pytest --cov --cov-report=term-missing` |
| Buyer pre-launch content gate | `make check-content` |
| Deploy/security check | `make check-deploy` |
| Requirements sync check | `make check-reqs` |
| Local smoke against running server | `make smoke` |
| Production smoke | `DEPLOY_URL=https://... make smoke-prod` |

## Selection Rules

| Change type | Minimum expected coverage |
| --- | --- |
| Pure render-path change in template/view/model | Add or update a unit/view test. |
| JS behavior, focus, keyboard, or body scroll lock | Add or update an e2e test. |
| Responsive fit or contrast-only change | Run the current screenshot audit workflow or record a manual review against the affected matrix rows. |
| Admin-controlled frontend change | Update frontend tests and the admin/config coverage that proves the input path or safety guard. |
| Launch-readiness or starter-content rule | Update `check_content_readiness` behavior and its tests. |

## Policy For Matrix Gaps

- `Covered` means the state has a named automated test or a named repeatable visual audit procedure.
- `Partial` means some evidence exists, but not enough to prove the whole state contract.
- `Gap` means the state is implemented but not currently proven by a reliable automated or scripted visual check.
- `Known debt` means the release explicitly accepts the remaining evidence gap and keeps it visible for follow-up.
- If a release touches a `Partial` or `Gap` row, that row must be reviewed in [RELEASE_CHECKLIST.md](RELEASE_CHECKLIST.md) before release.

## Current CI Gate

The repository CI job currently runs:

- `uv sync --group dev`
- `uv run ruff check .`
- `uv run mypy .`
- `uv run pytest --cov --cov-report=term-missing`
- `uv run pytest tests/e2e --override-ini="addopts=-v --tb=short" -m e2e --browser chromium`
- `uv run python manage.py check`
- `uv run python manage.py makemigrations --check --dry-run`
- `make check-deploy`
- `make check-reqs`

There is also a post-deploy smoke job in `.github/workflows/ci.yml` that runs on pushes to `main` when `DEPLOY_URL` is configured.
