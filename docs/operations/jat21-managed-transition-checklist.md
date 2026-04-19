# Jat21.com — Managed Service Transition Checklist

**Date:** 2026-04-19  
**Policy reference:** [managed-website-policy.md](managed-website-policy.md)

---

## Current known state

| Item | Value |
| --- | --- |
| Live source repo | `jat21architect-sys/jat21` |
| Production branch | `main` |
| Current Railway deployment | `f9b5e33a` — `fix(prod): replace DEFAULT_FILE_STORAGE with STORAGES dict for Django 5.2` |
| Domains | `jat21.com` and `www.jat21.com` — green on Railway |
| Template reference | `ksbk/kusse-folio` v1.4.2 (locked) — upstream reference only, not the live source |
| Railway: Wait for CI | Enabled |
| Template version on production | ❓ Unknown — `f9b5e33a` not yet cross-referenced to a kusse-folio tag |

---

## Target professional state

- Client (Jat21) owns: domain, brand assets, website content, business/customer data
- Kusse Studio manages: GitHub/repo, Railway hosting, Postgres, Cloudinary, SMTP, secrets, updates, monitoring
- Client has a named Django admin/editor account under their own email
- Kusse Studio has a named operator/admin account under a studio email
- Documented export/handover path exists and has been communicated to the client
- No single account is the only recovery path

---

## Phase 0 — Verification (do nothing until all are answered)

- [ ] **GitHub org `jat21architect-sys`:** Who owns this org? Studio or client?
      Can it be transferred to `ksbk` or a Kusse Studio org if needed?
- [ ] **Railway project:** Which Railway account owns the Jat21 project?
      Is Kusse Studio a team member? Is the client?
- [ ] **Cloudinary:** Check `CLOUDINARY_CLOUD_NAME` in Railway → Variables.
      Is this a dedicated Jat21 account or a shared studio account?
- [ ] **Domain / DNS:** Who controls the registrar account for `jat21.com`?
      Who can update DNS records if the Railway service URL changes?
- [ ] **SMTP / email:** What provider is configured in Railway env vars?
      Whose account is it? Who can rotate the credentials?
- [ ] **Django admin:** Log into `/admin/` → Users. What email is on the
      superuser account? Does the client have their own named account?
- [ ] **Template version:** Run `git tag --contains f9b5e33a` against
      `jat21architect-sys/jat21` or cross-reference the commit date against
      `ksbk/kusse-folio` history to confirm the baseline template version.

---

## Phase 1 — Backups before any change

Do not run migrations or change settings until these are done.

- [ ] Take a manual Postgres snapshot:
  ```bash
  pg_dump $DATABASE_URL > jat21_pre_transition_$(date +%Y%m%d_%H%M%S).sql
  ```
  Store the dump somewhere safe outside Railway (local machine, encrypted storage).
- [ ] Confirm Cloudinary media is intact: log into Cloudinary, confirm all
  project images, logos, and uploads are present and not orphaned.
- [ ] Document all current Railway environment variables (keys only — not values)
  so the full configuration can be reconstructed if needed.

---

## Phase 2 — Account and ownership decisions

Based on verification findings, decide:

- [ ] **GitHub:** Keep `jat21architect-sys/jat21` or move under Kusse Studio GitHub?
  - If moving: transfer the repo, update Railway source to the new location.
  - If keeping: add Kusse Studio GitHub account as an admin on the repo.
- [ ] **Railway:** Keep under current account or migrate to Kusse Studio Railway team?
  - If migrating: export the service config, reprovision under studio account,
    update DNS if the Railway domain changes.
  - If keeping: add Kusse Studio as a team member with deploy access.
- [ ] **Cloudinary:** Keep under current account or move to a studio-managed
  dedicated Jat21 account?
  - If moving: migrate all media assets, update `CLOUDINARY_*` env vars in Railway.
  - If keeping: confirm studio has operator access to the account.
- [ ] **SMTP:** Confirm provider and account. Add studio as admin if ongoing
  support is expected.
- [ ] **Domain:** Confirm client controls the registrar. Document the DNS records
  currently pointing `jat21.com` at Railway. No change needed unless infrastructure moves.

---

## Phase 3 — Account hygiene

- [ ] Create a named client Django admin/editor account under the client's email
  if one does not exist.
- [ ] Create a named Kusse Studio operator/admin account under a studio email
  if one does not exist.
- [ ] Confirm no shared anonymous superuser is the only admin account.
- [ ] Communicate login details to the client via secure channel (password manager
  share or equivalent — not plaintext email).

---

## Phase 4 — Template upgrade to v1.4.2 (after Phases 0–3 are complete)

Follow the [Jat21 v1.4.2 upgrade checklist](../ONBOARDING-DRILL-REPORT.md)
from the onboarding drill report. Key steps:

- [ ] Cross-reference `f9b5e33a` against `ksbk/kusse-folio` history to determine
  the upgrade diff — what migrations, model changes, and new features need to
  be applied.
- [ ] Apply relevant commits/changes from `ksbk/kusse-folio` into `jat21architect-sys/jat21`
  (cherry-pick or manual sync — do not blindly merge; review each change).
- [ ] Run health gate locally on the updated `jat21architect-sys/jat21` branch
  before pushing to production:
  ```bash
  uv run pytest -q
  uv run ruff check .
  uv run mypy .
  uv run python manage.py check
  uv run python manage.py makemigrations --check --dry-run
  ```
- [ ] Run migrations on production after verifying CI passes.
- [ ] Configure BrandSettings, SiteSettings module flags, contact visibility,
  and social links as per the upgrade checklist.
- [ ] Run `python manage.py check_content_readiness` — resolve all blockers.
- [ ] Smoke test all public pages including disabled module 404s.

---

## Phase 5 — Post-transition documentation

- [ ] Update the infrastructure ownership matrix with confirmed owners and access.
- [ ] Record the transition date, what changed, and who was notified.
- [ ] Confirm the client has received:
  - their named admin account login (via secure channel)
  - a plain-language explanation of what Kusse Studio manages and what they own
  - confirmation of their export/handover rights

---

## Client communication note

When communicating the managed service model to the client, use plain language:

> Kusse Studio handles all the technical side — hosting, deployments, updates,
> and backups. You stay in control of your domain, your content, and your
> business data. You have your own login to manage your site. If you ever want
> to move to a different provider or take over the technical side yourself,
> we can export everything and hand it over.

Do not use phrases like "we own your website" or "your site is on our servers
so you can't take it." The client always has the right to leave with their data.
