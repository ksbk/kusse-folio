# Release Checklist

Use this checklist before a tagged release or any buyer-facing delivery. This file is documentation-aware and complements the repo-root [RELEASE.md](../../RELEASE.md).

## 1. Documentation Sync

- [ ] Shared specs match current implementation for any changed global, typography, layout, hero, or navbar behavior.
- [ ] Every changed required state still has a matching row in [TEST_MATRIX.md](TEST_MATRIX.md).
- [ ] Any configurable behavior changed in code is queued for Phase 3 admin docs; do not silently ship undocumented config changes.
- [ ] Known docs debt remains visible if any exists.
  Current status:
  - Open evidence gaps and `Partial` rows remain tracked in `docs/qa/TEST_MATRIX.md` and in spec known-gap sections.
  - Do not mark docs drift as closed while a checklist item, matrix row, or spec still points to retired files or commands.

## 2. Automated Gate

### 2a. CI-safe checks (no populated database required)

- [ ] `make health`
- [ ] `make test-e2e`
- [ ] `make check-deploy`
- [ ] `make check-reqs`

### 2b. Buyer pre-launch gate (requires a configured, populated database)

These commands require a running instance with real content. They are not CI-safe and must not be added to `make health` or any CI-equivalent gate. Run them as part of the buyer's deploy checklist or as a pre-launch handoff step.

- [ ] `make check-content`
  Verifies database-backed launch content and public-facing setup, including the public contact email shown on the site. Requires a populated database (projects, site settings, contact config).
- [ ] `DEPLOY_URL=https://... make smoke-prod`
  Verifies the live deployed routes and assets against the real launch URL after deployment.

## 3. State Coverage Review

- [ ] Review all `Partial` and `Gap` rows in [TEST_MATRIX.md](TEST_MATRIX.md) that are touched by this release.
- [ ] If shared UI behavior changed, run the current screenshot audit workflow (`uv run python scripts/take_screenshots.py`, then `uv run python scripts/analyse_screenshots.py`) when practical, or record a manual visual review against the affected matrix rows.

## 4. Smoke

- [ ] Run `make smoke` against the staging or local verification instance.
  This verifies the rendered public routes and key assets on a running instance; it does not replace `make check-content` or `make check-deploy`.
  Use a prod-like verification instance for this step. A plain `DEBUG=True` dev server will not prove the branded 404 path used in the smoke check.
## 5. Release Notes And Follow-Up

- [ ] Update the repo-root release notes process in [RELEASE.md](../../RELEASE.md) if the release workflow itself changed.
- [ ] Carry forward any unresolved docs/test debt explicitly in the PR or release notes; do not let it disappear from the checklist just because the code shipped.
