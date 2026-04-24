# Kusse Folio — Product Scope

**Locked:** 2026-04-24

---

## Required core pages

These five pages define the **minimum valid Kusse Folio product**. Every build
ships with them. They must pass all functional and readiness checks.

| Page | Route pattern | App |
|---|---|---|
| Home | `/` | `pages` |
| About | `/about/` | `pages` |
| Projects | `/projects/` | `projects` |
| Contact | `/contact/` | `contact` |
| Privacy | `/privacy/` | `pages` |

Starter must feel complete, not crippled. Projects are core to all tiers.

---

## Portfolio Presets

`SiteSettings.portfolio_preset` controls reusable homepage and navigation emphasis
without creating separate codebase branches.

| Preset | Purpose |
|---|---|
| `generic` | Default professional portfolio behavior: projects-first homepage and navigation. |
| `service` | Reserved service / consultant emphasis for future refinement. |
| `academic` | Academic / research portfolio behavior: research and publications are prioritized when enabled. |

The **Academic / Research Portfolio** variant is suitable for researchers, PhD
students, lecturers, scientists, consultants, and technical experts who need a
public site for research areas, publications, selected projects, CV, teaching,
speaking, consulting, and collaboration enquiries.

`drkusse.com` is the first reference implementation of this reusable academic
variant. Dr. Kusse-specific content should live in content, seed, and config
layers rather than in hardcoded template logic.

---

## Optional Modules

Optional modules are off by default for new builds unless a seed/profile enables
them. They must not appear in nav, readiness checks, or buyer onboarding as if
they are required when disabled.

| Module | `SiteSettings` flag | Implementation state |
|---|---|---|
| Blog | `blog_enabled` | Implemented |
| Services | `services_enabled` | Implemented |
| Research | `research_enabled` | Implemented |
| Publications | `publications_enabled` | Implemented |
| Resume / CV | `resume_enabled` | Implemented |
| Testimonials | `testimonials_enabled` | Implemented |

**Rule:** A module flag is exposed in admin only when the corresponding public
surface exists. A buyer should never be able to enable a module and see nothing
happen.

---

## Commercial Packaging

Kusse Folio is designed to support tiered commercial marketing from a single
codebase. Presets are applied by the settings/activation/seed layer, not by
separate codebase branches.

| Tier | Preset | Included modules |
|---|---|---|
| **Starter** | `generic` | Home, About, Projects, Contact, Privacy |
| **Pro** | `generic` | Starter + Blog, Resume / CV |
| **Academic / Research Portfolio** | `academic` | Starter + Research, Publications, Resume / CV |
| **Consultant** | `service` | Starter + Services, Blog |

Academic sites may still use Projects for applied work, selected case studies,
fieldwork, tools, public reports, consulting outputs, or technical projects.
Services remain optional and should only be enabled when the site has a real
service/consulting offer.

---

## Nav Rule

Optional module links **must not appear in the primary or footer navigation
unless that module is explicitly enabled** for the build.

Default generic nav remains projects-first. Academic preset nav prioritizes:
Research, Publications, Projects, About, CV, Contact, with optional Services and
Blog included only when enabled.

---

## Homepage Rule

Default generic behavior remains projects-first. Academic preset behavior may
point the primary homepage CTA and scroll target to Research when enabled, or to
Publications when Research is disabled and Publications is enabled. This is a
reusable preset behavior, not a one-off personal-site override.

---

## Readiness Rule

`check_content_readiness` and the corresponding admin Launch Readiness panel must
only surface checks for optional modules when those modules are enabled.

When Research, Publications, or Resume / CV are enabled, readiness should check
for visible academic content. Disabled modules must produce zero warnings or
blockers.

---

## Naming

In all product language, docs, and buyer-facing copy:

- Use **Blog**, not Writing.
- Use **Resume / CV** in admin and docs; **CV** may be used as the short nav label.
- Use **Academic / Research Portfolio** for the academic tier/variant.

The internal URL namespace (`blog`) and legacy `/writing/` route can stay as-is
pending an explicit route migration decision.

---

## Explicit v0.2 Deferrals

Academic Variant v0.1 intentionally does **not** include:

- full structured CV models
- BibTeX/RIS export
- advanced publication metadata or import systems
- complex collaborators/funders/grants modeling
- deep research-publication relationship modeling
