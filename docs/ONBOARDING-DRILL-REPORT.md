# Onboarding Drill Report — v1.4.1

**Date:** 2026-05-02  
**Tested against:** kusse-folio v1.4.1  
**Method:** Fresh DB → migrate → seed_demo → superuser → 9-phase programmatic drill (114 checks) + manual admin inspection  
**Drill script:** `scripts/onboarding_drill.py`

---

## Summary

| Category | Count |
| --- | --- |
| Drill checks run | 114 |
| Checks passed | 114 |
| Blockers found (now fixed) | 4 |
| Polish items (not fixed) | 6 |
| Upgrade path warning needed | 1 |

Fresh install from a clean clone works end-to-end. All three buyer scenarios
(service business, academic/professional, portfolio/developer) resolve and route
correctly. All module flag combinations tested — enable/disable logic in nav,
footer, homepage, and URL routing is correct throughout.

---

## Blockers — Fixed in this release (v1.4.1)

### 1. SETUP.md Phase 3 — stale About Profile field names

**Severity:** High — a buyer following SETUP.md will not find the fields in admin.

SETUP.md Phase 3 (About Profile table) and the pre-launch checklist (Phase 7) both
referenced field names from before the v1.1.0 rename. Buyers following the guide
would look for admin fields that no longer exist under those names.

| Was in SETUP.md | Current field name |
| --- | --- |
| `practice_structure` | `professional_context` |
| `one_line_practice_description` | `one_line_bio` |
| `practice_summary` | `bio_summary` |
| `project_leadership` | `work_approach` |

**Fixed:** Both Phase 3 table and the Phase 7 pre-launch checklist updated.

---

### 2. CUSTOMIZATION.md — stale `Service` model references

**Severity:** Low — internal doc only, but causes confusion when cross-referenced.

Two rows in `docs/admin/CUSTOMIZATION.md` referenced `Service` (removed in v1.1.0)
instead of `ServiceItem` (re-added in v1.2.0).

**Fixed:** Both rows updated to `ServiceItem`.

---

### 3. Admin index subtitle — Brand Settings missing from start-here sequence

**Severity:** Low — buyers who skip Brand Settings on first run miss a key setup step.

The admin `index_title` read:
> "Start here: Site Settings → About Profile → Services → Projects"

Brand Settings (added in v1.4.0) was not in the sequence. Services is contextual
(not all buyers use it), so it also doesn't belong in a universal start-here prompt.

**Fixed:**
> "Start here: Site Settings → Brand Settings → About Profile → Projects"

---

### 4. CHANGELOG — missing v1.2.0, v1.3.0, v1.4.0, v1.4.1

**Severity:** High for buyers evaluating updates — four releases with significant
features (services, testimonials, research, publications, resume, brand
customization) had no release notes.

**Fixed:** All four entries written and added to CHANGELOG.md.

---

## Upgrade Path Warning — v1.1.x → v1.2.0+

**Severity:** High for upgraders — fresh installs unaffected.

The `apps/services` app was removed in v1.1.0 and re-added in v1.2.0 with a new
model (`ServiceItem`) and a new migration (`services.0001_initial`). Django's
migration recorder does not remove old records when an app is unregistered, so
databases that ran migrations under v1.0.x–v1.1.1 have a stale
`services.0001_initial` entry. Django sees this entry and skips the new migration,
leaving `services_serviceitem` uncreated. Running `seed_demo` then crashes with
`no such table: services_serviceitem`.

**Documented in:** CHANGELOG.md [1.2.0] Upgrade note, with recovery commands.

**Recovery for affected databases:**
```bash
uv run python manage.py shell -c "
from django.db import connection
cur = connection.cursor()
cur.execute(\"DELETE FROM django_migrations WHERE app='services'\")
print('Removed stale services migration records — safe to migrate now')
"
uv run python manage.py migrate
```

---

## Polish Items — Carry to v1.5.0

### P1. Homepage empty-state when module enabled without content

If a buyer enables `services_enabled`, `research_enabled`, or `publications_enabled`
before adding any content, the homepage renders the section heading and "All
Services / All Research / All Published Work" link with an empty grid below it.
The template needs an `{% if items %}` guard on the outer section so the entire
block is suppressed when no content exists.

**Affected templates:**
- `apps/pages/templates/pages/home.html` — Services preview (~line 72), Research
  preview (~line 113), Publications preview (~line 136)

---

### P2. Hardcoded page hero h1 text on module list pages

The h1 on three module list pages is not admin-manageable and not documented as a
buyer-facing limitation:

| Page | Hardcoded h1 |
| --- | --- |
| Services list | "What We Offer" |
| Research list | "Research Projects" |
| Publications list | "Published Work" |

**Action:** Either add a `page_title` field to each module's SiteSettings block,
or document these as `code-only (simple editorial change)` surfaces in
CUSTOMIZATION.md.

---

### P3. No per-module meta descriptions

Services, Research, Publications, and Resume pages all fall back to
`SiteSettings.meta_description` (the homepage meta). Buyers with distinct
offerings for each surface have no way to set page-specific SEO copy without
editing templates.

**Action for v1.5.0:** Add `services_meta_description`, `research_meta_description`,
`publications_meta_description`, and `resume_meta_description` to `SiteSettings`.
Wire to the respective page `<meta name="description">` tags.

---

### P4. Resume page is minimal — no structured sections

`apps/resume/templates/resume/page.html` renders headline, summary, and CV
download only. There are no experience, skills, or education sections in the
template even though `AboutProfile.education` and `AboutProfile.supporting_facts`
contain relevant data.

**Action:** Evaluate whether Resume page should pull from `AboutProfile` fields or
whether `ResumeProfile` needs its own structured section fields.

---

### P5. `seed_demo` enables all modules — not communicated in SETUP.md

`seed_demo` sets all six optional module flags to `True` so buyers see the full
site immediately. SETUP.md does not mention this, so buyers who only want a service
business site may be confused to find Research, Publications, and Resume links in
the nav.

**Action:** Add one sentence to SETUP.md Phase 0 (after the seed_demo command):
> `seed_demo` enables all optional modules so you can preview the full site.
> Disable any you don't need in Admin → Site Settings → Optional modules.

---

### P6. Admin workflow guide doesn't mention academic/resume path

The admin `index_title` and SETUP.md Phase 4 give good guidance for service
businesses, but academic/professional buyers (Research + Publications + Resume) have
no equivalent "do this in order" guidance.

**Action:** Add a short "Academic / professional portfolio" track to SETUP.md
Phase 4 alongside the existing Services track.

---

## Fresh Install Drill Results

### Phase 0 — Baseline seeded state
All public routes return 200. Nav shows correct links for all enabled modules.
Homepage renders all six module sections. Admin accessible. `check_content_readiness`
reports 9 blockers (all expected demo content) and 4 warnings. Passes cleanly.

### Phase 1 — All modules off
All six flags disabled. Nav and footer show Projects, About, Contact only. All
module list URLs return 404. Homepage shows no optional sections. All 16 checks pass.

### Phase 2 — Service business (services + testimonials)
Services list, detail, and enquiry links work. Testimonials section renders on
homepage. Module flag toggling in nav/footer is correct. All 12 checks pass.

### Phase 3 — Academic/professional (research + publications + resume)
Research list renders 3 records. Publications list renders 3 records. Resume page
renders ResumeProfile headline and summary. All module routes active. 9 checks pass.

### Phase 4 — Portfolio/developer (blog + resume)
Blog post list and detail render. Resume page active. Services/research/publications
suppressed. Blog post URL slug routing correct. Checks pass.

### Phase 5 — Brand customization
All 5 typography presets save and validate correctly. All 6 color presets save
correctly (including custom hex). Hex validation rejects invalid values. All 3
visual style options save. Logo display mode enum validated. All checks pass.

### Phase 6 — Contact visibility controls
`show_email=False` correctly suppresses email from contact page and footer.
All toggle combinations behave correctly.

### Phase 7 — Core page routes
Homepage, About, Contact, Studio (if relevant) all return 200.
Unknown project slug returns 404. Correct.

### Phase 8 — Admin registration
All 12 registered models confirmed in admin. `ProjectImage` is inline-only (not
standalone registered) — expected and correct.

### Phase 9 — `check_content_readiness`
9 blockers (all expected demo content), 4 warnings (og_image, per-page meta, portrait).
Command exits with code 1. CI-friendly. Passes cleanly.

---

## Health Gate

| Check | Result |
| --- | --- |
| `uv run pytest -q` | 384 passed, 0 failed |
| `uv run ruff check .` | All checks passed |
| `uv run mypy .` | Success: no issues in 171 source files |
| `uv run python manage.py check` | No issues (0 silenced) |
| `uv run python manage.py makemigrations --check --dry-run` | No changes detected |

All five gates pass. The drill script (`scripts/onboarding_drill.py`) uses the
required Django shell pattern — `django.setup()` must precede all app imports — so
`E402` and `I001` are suppressed for that file via `per-file-ignores` in
`pyproject.toml`. All other code under `apps/`, `config/`, and `tests/` passes
without per-file exceptions.

---

## DB Note

The drill DB (`db.sqlite3`) is a fresh install, post-drill, with `seed_demo` data.
The original development DB is backed up at `db.sqlite3.drill-backup`. Restore it
if needed with:

```bash
mv db.sqlite3.drill-backup db.sqlite3
```
