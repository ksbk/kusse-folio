# Buyer Setup Guide

A step-by-step checklist for taking this template from fresh install to live site.
Work through each phase in order. Kusse Folio is an opinionated professional portfolio
template, not a no-code site builder, so the full setup path includes admin content,
launch-critical environment configuration, optional integrations, and some code-level
customization.

---

## Phase 1 — First run (local)

**Goal:** Get the site running locally so you can see it before making any changes.

```bash
# 1. Clone and install
git clone <repo-url>
cd <project-directory>
uv sync --group dev

# 2. Create your environment file
cp .env.example .env
```

Open `.env` and set `SECRET_KEY`:

```bash
uv run python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Paste the output as the value. Leave everything else as-is for now.

```bash
# 3. Create the database
uv run python manage.py migrate

# 4. Create your admin account
uv run python manage.py createsuperuser

# 5. Load starter/demo content so the site renders on first visit
uv run python manage.py seed_demo

# 6. Start the dev server
uv run python manage.py runserver
```

Visit **<http://127.0.0.1:8000>** and confirm the site loads.
Visit **<http://127.0.0.1:8000/admin>** and log in with the credentials you just created.

`seed_demo` creates or updates the shipped starter/demo dataset so a fresh install
renders immediately. It currently seeds:

- `Site Settings` — including the optional-module flags
- `Brand Settings`
- `About Profile`
- four `Service` records
- three `Research Project` records
- three `Publication` records
- one `Resume / CV Profile`
- one published `Post` for the Writing module
- eleven example `Project` records (seven featured)
- four `Testimonial` records: three project-linked and one standalone homepage testimonial
- the tracked demo-media bundle when available

`seed_demo` does **not** configure production email delivery, production media storage,
or deployment settings. It is starter content only.

> **Note:** If you run `make check-content` now, you will see several blockers
> — that is expected. The starter/demo content is intentionally placeholder; the
> blockers are your checklist for Phase 7. Work through Phases 2–6 first, then
> run the check.

---

## Before You Customize

Before replacing demo content, read the canonical customization reference:
[docs/admin/CUSTOMIZATION.md](docs/admin/CUSTOMIZATION.md).

That document is the single source of truth for which surfaces are:

- `admin-managed`
- `env/config-managed — required for launch`
- `env/config-managed — optional integration`
- `code-only (simple editorial change)`
- `code-only (behavior-coupled / risky)`
- `intentionally opinionated`

## Three Customization Tracks

- `admin-managed`: the core public content workflow in Django admin
- `env/config-managed — required for launch`: contact delivery, production media storage,
  and production Django settings
- `env/config-managed — optional integration`: tooling such as Sentry
- `code-only (simple editorial change)` and `code-only (behavior-coupled / risky)`:
  visible copy, assets, structure, and logic that still require code edits; see the
  canonical matrix for the exact split

> **Common assumptions to avoid**
>
> - Nav labels and routes are not `admin-managed`.
> - Project tags are `admin-managed`, but the filter behavior and URL/query-param shape are code-defined.
> - Contact form structure and dropdown choices are code-defined.
> - Some CTA and editorial strings still require template edits.
> - Production media and contact delivery require config, not admin content.

## Launch-Critical Configuration Checklist

Before launch, confirm all of the following:

- public content has replaced the starter/demo content in admin
- `CONTACT_EMAIL` and SMTP settings are configured so enquiries reach a monitored inbox
- production media storage credentials are configured before accepting real uploads
- production Django settings such as `DATABASE_URL`, `ALLOWED_HOSTS`, and
  `CSRF_TRUSTED_ORIGINS` are set for the live domain
- `make check-deploy` and `check_content_readiness` pass against the intended environment

## Optional Integrations

These do not block launch:

- `google_analytics_id` in `Site Settings`
- `SENTRY_DSN` and related Sentry settings

---

## Phase 2 — Brand and site identity

### Admin → Site Settings

Replace every placeholder with your real information.

| Field | What to enter | Notes |
| --- | --- | --- |
| `site_name` | Your practice name | e.g. "Alex Morgan Design" |
| `tagline` | One-line positioning statement | Shown in the homepage hero and footer |
| `hero_label` | Optional short descriptor above the homepage title | e.g. "Design & Research" |
| `nav_name` | Optional short navbar brand override | Use if the full `site_name` is too long or the automatic monogram is weak |
| `logo` | Upload your logo | Replaces text branding in the navbar |
| `contact_email` | Public email shown on the site | Shown in the footer and contact page. Contact-form notifications are configured separately via `CONTACT_EMAIL` |
| `phone` | Your contact number | Optional — leave blank to hide |
| `location` | City, Country | Displayed in footer and contact page |
| `address` | Full postal address | Stored in admin only in the current implementation |
| `contact_response_time` | Public response-time wording | Used on the Contact page and success state, e.g. "two working days" |
| `og_image` | Default social share image | Used when no project cover image exists — 1200 × 630 px recommended |
| `meta_description` | Homepage SEO description | Keep under 160 characters |

**Per-page SEO descriptions** (all optional — add if you want control over how each
page appears in search results):

- `about_meta_description`
- `projects_meta_description`
- `contact_meta_description`

If you do set a page-specific meta description, make sure it matches the current
studio identity. The launch-readiness check now flags stale per-page metadata
that still names an old demo studio.

**Social links — quick setup path** (all optional):

- `linkedin_url`
- `instagram_url`
- `facebook_url`
- `behance_url`
- `issuu_url`

These inline `Site Settings` URL fields are the fastest setup path and work well if
you only need simple text links in the footer and contact page.

If you want more controlled social rendering, use **Admin → Social Links** instead:

- create one `Social Link` record per platform
- set `label`, `url`, and `icon_slug`
- use this path when you choose Brand Settings → `social_links_display` = `icons` or `icons_text`

When active `Social Link` records exist, the footer uses them in preference to the
inline URL fields. For icon-based display modes, `icon_slug` must be set on each entry.

**Analytics** (optional):

- `google_analytics_id` — paste your GA4 Measurement ID (e.g. `G-XXXXXXXXXX`)

### Admin → Brand Settings

Use this screen to tune how the current brand is rendered without changing the site
structure.

| Field | What to enter | Notes |
| --- | --- | --- |
| `logo_display_mode` | `auto`, `transparent`, or `safe_card` | Controls the navbar wrapper used around the uploaded logo |
| `typography_preset` | Choose the closest built-in type pairing | Applied site-wide via CSS custom properties |
| `color_preset` | Choose a named preset | Controls accent color surfaces such as buttons, borders, and highlights |
| `accent_color_custom` | Optional 6-digit hex value such as `#B45309` | Only used when `color_preset` is `custom` |
| `visual_style` | `crisp`, `balanced`, or `soft` | Controls corner rounding across cards, buttons, and images |
| `social_links_display` | `text`, `icons`, or `icons_text` | `icons` and `icons_text` work best with `Social Link` records that have `icon_slug` set |

---

## Phase 3 — About page

### Admin → About Profile

Start with the fields that shape the public identity of the practice:

| Field | What to enter | Notes |
| --- | --- | --- |
| `identity_mode` | `studio` or `person` | Choose whether the page introduces the studio or a named principal |
| `principal_name` | Public principal name | Required only for person-led mode |
| `principal_title` | Public role/title | Used in the hero meta line for person-led mode |
| `professional_context` | Truthful short descriptor | e.g. "Solo practitioner" or "Small studio" |
| `one_line_bio` | Short public one-liner | Shown in the About hero |

Then complete the main narrative:

| Field | What to enter | Notes |
| --- | --- | --- |
| `bio_summary` | What the practice does and what kind of work it takes on | Main opening prose block |
| `work_approach` | How projects are led and where collaborators fit | Secondary narrative block |
| `approach` | Short practical approach statement | 2–3 sentences is ideal |
| `closing_invitation` | Short closing CTA copy | If kept under 80 characters it becomes the CTA heading |

Then fill the credibility block:

| Field | What to enter | Notes |
| --- | --- | --- |
| `professional_standing` | Registration or professional standing | Publicly shown when complete |
| `education` | One fact per line | e.g. degrees, formal training |
| `supporting_facts` | One factual proof point per line | e.g. sectors worked in, delivery scope, awards if real |
| `experience_years` | Your actual years of practice | This renders publicly as `N+ years in practice` |

Portrait and file options:

| Field | What to enter | Notes |
| --- | --- | --- |
| `portrait_mode` | `text_only` or `portrait` | Use text-only until you have a real portrait ready |
| `portrait` | Upload a real portrait | Required for the portrait column to render |
| `cv_file` | Optional PDF profile/CV | Only appears when the portrait column is visible |

---

## Phase 4 — Services

### Admin → Services

Four starter service records are loaded by `seed_demo`. Edit them to match your
actual offering, or delete and create your own.

For each service:

| Field | What to enter |
| --- | --- |
| `name` | Service name, e.g. "Briefing & Feasibility" |
| `short_description` | The short summary shown on service cards and previews |
| `long_description` | Optional longer explanation shown on the Services page |
| `order` | Controls display order; lower numbers appear first |
| `active` | Uncheck to hide a service without deleting it |

### Other optional modules

The optional modules are controlled in **Admin → Site Settings → Optional modules**.
Starter content is seeded for the modules that are enabled by default, but each module
still needs to be reviewed and replaced with your own material before launch.

| Module | Admin location | Notes |
| --- | --- | --- |
| `Research` | `Admin → Research Projects` | `seed_demo` creates three starter records |
| `Publications` | `Admin → Publications` | `seed_demo` creates three starter records |
| `Resume / CV` | `Admin → Resume / CV Profile` | `seed_demo` creates one starter profile |
| `Blog / Writing` | `Admin → Posts` | `seed_demo` creates one modest published starter post so the route is visible |

---

## Phase 5 — Projects

### Admin → Projects

`seed_demo` loads eleven example projects, seven of them featured. Replace the
demo records with your real work before launch, or add your own projects directly
in admin.

For each project:

### Core

| Field | What to enter |
| --- | --- |
| `title` | Project name |
| `slug` | Usually leave the autogenerated slug unless you need a specific URL |
| `short_description` | 1–2 sentences for cards and search results (under 160 characters ideal) |
| `tags` | Comma-separated tags, e.g. `housing` or `housing, residential` |
| `status` | Completed / In Progress / Concept / Competition Entry |

### Metadata

| Field | What to enter |
| --- | --- |
| `location` | Where the project is located |
| `year` | Year completed (or anticipated) |
| `client` | Client name — leave blank if confidential |
| `area` | Floor area, e.g. `2 400 m²` |
| `services_provided` | Scope delivered, e.g. "Concept design through construction administration" |

**Narrative** (all optional — fill as many as apply)

| Field | What to enter |
| --- | --- |
| `overview` | Project introduction |
| `challenge` | The design challenge or brief constraints |
| `concept` | The core design idea |
| `process` | Design and construction process |
| `outcome` | Result and impact |

### Media

| Field | What to enter |
| --- | --- |
| `cover_image` | Hero image — at least 1600 × 900 px, JPEG or WebP |
| `image` (Project Images inline) | Upload each gallery/supporting image |
| `image_type` | Choose `gallery`, `plan`, `section`, `sketch`, `detail`, or `render` |
| `caption` | Optional caption shown with the image |
| `alt_text` | Optional descriptive alt text; recommended for accessibility |
| `order` | Controls image order within the gallery/supporting media |

### Display flags

| Field | What to enter |
| --- | --- |
| `featured` | Check to show this project on the homepage |
| `order` | Controls list order within the portfolio; lower numbers appear first |

**SEO overrides** (optional)

| Field | What to enter |
| --- | --- |
| `seo_title` | Overrides the project title in browser tab and search (under 60 characters) |
| `seo_description` | Overrides `short_description` in search results (under 160 characters) |

**Testimonials** (optional — added inline on the project record)

Each project can have testimonials attached inline. Add the author name, role, company,
quote, order, and active state.

### Adding many projects from local files

The `bootstrap_project` and `import_project_images` commands can create projects and
attach gallery images from local files. Both commands require absolute file paths.
Always run `--dry-run` first:

```bash
uv run python manage.py bootstrap_project \
  --dry-run \
  --title "House Aldea" \
  --tags "housing, residential" \
  --short-description "Private residence on a constrained urban site." \
  --cover /absolute/path/to/cover.jpg \
  --gallery /absolute/path/to/gallery-01.jpg /absolute/path/to/gallery-02.jpg

uv run python manage.py import_project_images \
  --dry-run \
  --project house-aldea \
  --gallery /absolute/path/to/gallery-03.jpg /absolute/path/to/gallery-04.jpg
```

---

## Phase 6 — Email

Contact form submissions are always saved to the database and visible in Admin → Contact
Inquiries, regardless of whether email is configured. **If you skip this phase or leave
`CONTACT_EMAIL` unset, submissions will be saved but no notification email will be sent to
you.** Configure `CONTACT_EMAIL` before launch to enable delivery notifications. This is
`env/config-managed — required for launch`.

To also set up email notifications, configure an SMTP backend and set the following
variables. There are three separate email roles in this template:

- `Site Settings.contact_email`: the public email shown on the site
- `CONTACT_EMAIL`: the inbox that receives contact-form notification emails
- `DEFAULT_FROM_EMAIL`: the sender shown on outgoing notification emails

Open `.env` (or your production environment variables) and set:

```dotenv
# Switch to SMTP
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-smtp-username
EMAIL_HOST_PASSWORD=your-smtp-password

# Address in the From field of outgoing emails
DEFAULT_FROM_EMAIL=Your Name <hello@yourdomain.com>

# Address that receives contact form notifications — must be your monitored inbox
CONTACT_EMAIL=hello@yourdomain.com
```

Verify by submitting the contact form locally and checking that you receive the email.

---

## Phase 6.5 — Media storage for launch

Production uploads require Cloudinary-backed media storage before launch. This is
`env/config-managed — required for launch`.

Set these three variables in the production environment before accepting any uploaded
content:

```dotenv
CLOUDINARY_CLOUD_NAME=your-cloud-name
CLOUDINARY_API_KEY=your-api-key
CLOUDINARY_API_SECRET=your-api-secret
```

Without them, uploaded media in production will not be launch-ready. Run `make check-deploy`
after setting the variables; the production checks validate that the required credentials
are present.

---

## Phase 7 — Content readiness check

Run this before deploying. It scans your database for required fields that are still blank
or still set to starter/demo values:

```bash
uv run python manage.py check_content_readiness
```

The command uses two output levels:

| Output | Meaning | Action |
| --- | --- | --- |
| `✗` (blocker) | Must be fixed before launch — site will look broken or still contain demo values | Fix before deploying |
| `⚠` (warning) | Does not block launch but degrades quality or trust | Fix if time allows |
| All clear | No issues found | Proceed to Phase 8 |

The command exits with code `1` if any blocker is present (CI-friendly).

**Common first-run blockers and where to fix them:**

| Blocker message | Where to fix |
| --- | --- |
| `site_name` is still the demo value | Admin → Site Settings → Identity |
| `contact_email` is still the demo value | Admin → Site Settings → Contact |
| `one_line_bio` is blank or demo copy | Admin → About Profile → Identity |
| `bio_summary` is blank or demo copy | Admin → About Profile → Content |
| Demo project titles detected | Admin → Projects — replace or delete the seeded examples |

---

## Phase 8 — Production environment

Set these variables in your hosting environment (e.g. Railway → Variables). See [README.md §Environment variables](README.md#environment-variables) for the full annotated reference.

The minimum required production variables are: `SECRET_KEY`, `DEBUG=False`, `DJANGO_SETTINGS_MODULE=config.settings.prod`, `ALLOWED_HOSTS`, `DATABASE_URL`, `CSRF_TRUSTED_ORIGINS`, `CONTACT_EMAIL`, and the SMTP email settings.

**Media storage (required for uploads):** The production settings module routes uploaded media through Cloudinary. Set `CLOUDINARY_CLOUD_NAME`, `CLOUDINARY_API_KEY`, and `CLOUDINARY_API_SECRET` before accepting any uploaded content. Without them, all image uploads — project covers, gallery images, and the About portrait — are not launch-ready. Run `make check-deploy` after setting variables; the production checks confirm the required credentials are present.

**Optional integrations:** `SENTRY_DSN` (error tracking) and `google_analytics_id` in Site Settings (analytics) can be added at any time after launch without affecting core functionality.

After setting variables and deploying, verify production Django settings:

```bash
make check-deploy
# or: uv run python manage.py check --deploy
```

Fix any warnings before accepting live traffic.

---

## Phase 9 — Go live

Run the content readiness check one final time against production:

```bash
DJANGO_SETTINGS_MODULE=config.settings.prod uv run python manage.py check_content_readiness
```

Then smoke-check the live site:

```bash
SMOKE_BASE_URL=https://yourdomain.com make smoke
```

This confirms the main pages return HTTP 200 and no obvious errors appear.

---

## Quick reference — admin sections

| Admin section | What it controls |
| --- | --- |
| **Site Settings** | Brand, contact details, social links, SEO, analytics |
| **About Profile** | About page content and portrait |
| **Services** | Services listing page |
| **Projects** | Portfolio grid and individual project pages |
| **Contact Inquiries** | Submitted enquiries (read and manage) |

## Quick reference — management commands

See [README.md §Management commands](README.md#management-commands) for the full reference including safety notes, idempotency status, and key flags for each command.
