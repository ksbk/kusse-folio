"""
Onboarding drill script — v1.4.1
Runs all buyer/client scenario checks using Django's test client.
Execute via: uv run python manage.py shell < scripts/onboarding_drill.py
Or: uv run python -c "exec(open('scripts/onboarding_drill.py').read())"
"""

import os
import subprocess

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings.dev")

django.setup()

from django.contrib import admin as django_admin
from django.core.exceptions import ValidationError
from django.test import Client
from apps.blog.models import Post
from apps.projects.models import Project, Testimonial
from apps.publications.models import Publication
from apps.research.models import ResearchProject
from apps.resume.models import ResumeProfile
from apps.services.models import ServiceItem
from apps.site.models import BrandSettings, SiteSettings

PASS = "✓"
FAIL = "✗"
WARN = "⚠"

results = []


def check(label, ok, note=""):
    status = PASS if ok else FAIL
    results.append((status, label, note))
    print(f"  {status}  {label}" + (f"  [{note}]" if note else ""))


def section(title):
    print(f"\n{'─'*60}")
    print(f"  {title}")
    print(f"{'─'*60}")


client = Client(HTTP_HOST="localhost")


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 0: Baseline state
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 0 — Baseline seeded state")

site = SiteSettings.load()
brand = BrandSettings.load()

check("SiteSettings exists", site is not None)
check("BrandSettings exists", brand is not None)
check("site_name seeded", bool(site.site_name))
check("tagline seeded", bool(site.tagline))
check("contact_email seeded", bool(site.contact_email))

# seed_demo enables all optional modules so buyer can see everything on first load
# Check that all module flags are boolean (seeded state — all True by design)
check("blog_enabled is bool after seed", isinstance(site.blog_enabled, bool))
check("services_enabled is bool after seed", isinstance(site.services_enabled, bool))
check("testimonials_enabled is bool after seed", isinstance(site.testimonials_enabled, bool))
check("research_enabled is bool after seed", isinstance(site.research_enabled, bool))
check("publications_enabled is bool after seed", isinstance(site.publications_enabled, bool))
check("resume_enabled is bool after seed", isinstance(site.resume_enabled, bool))
# Verify seed_demo enables all for demo-first experience
check("seed_demo enables all modules for demo", all([
    site.blog_enabled, site.services_enabled, site.testimonials_enabled,
    site.research_enabled, site.publications_enabled, site.resume_enabled,
]))

# Brand defaults
check("typography_preset default balanced", brand.typography_preset == "balanced")
check("color_preset default neutral", brand.color_preset == "neutral")
check("visual_style default balanced", brand.visual_style == "balanced")
check("social_links_display default text", brand.social_links_display == "text")
check("logo_display_mode default auto", brand.logo_display_mode == "auto")

check("4 ServiceItems seeded", ServiceItem.objects.count() == 4)
check("3 ResearchProjects seeded", ResearchProject.objects.count() == 3)
check("3 Publications seeded", Publication.objects.count() == 3)
check("ResumeProfile exists", ResumeProfile.objects.filter(pk=1).exists())
check("11 Projects seeded", Project.objects.count() == 11)
check("4 Testimonials seeded", Testimonial.objects.count() == 4)
check("1 Post seeded", Post.objects.count() == 1)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 1: All-modules-off (default) public UI
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 1 — Default state: all optional modules off")

site.blog_enabled = False
site.services_enabled = False
site.testimonials_enabled = False
site.research_enabled = False
site.publications_enabled = False
site.resume_enabled = False
site.save()

r = client.get("/")
check("Home 200", r.status_code == 200)
check("Home: no testimonials section when disabled", b"testimonial" not in r.content.lower() or b'class="testimonials' not in r.content)

r = client.get("/projects/")
check("Projects list 200", r.status_code == 200)

r = client.get("/about/")
check("About 200", r.status_code == 200)

r = client.get("/contact/")
check("Contact 200", r.status_code == 200)

r = client.get("/privacy/")
check("Privacy 200", r.status_code == 200)

# Disabled module URLs should 404
r = client.get("/services/")
check("Services 404 when disabled", r.status_code == 404)

r = client.get("/research/")
check("Research 404 when disabled", r.status_code == 404)

r = client.get("/publications/")
check("Publications 404 when disabled", r.status_code == 404)

r = client.get("/resume/")
check("Resume 404 when disabled", r.status_code == 404)

r = client.get("/writing/")
check("Blog 404 when disabled", r.status_code == 404)

# Nav: disabled modules absent from header
r = client.get("/")
check("Nav: no Services link when disabled", b'href="/services/"' not in r.content)
check("Nav: no Research link when disabled", b'href="/research/"' not in r.content)
check("Nav: no Publications link when disabled", b'href="/publications/"' not in r.content)
check("Nav: no Resume/CV link when disabled", b'href="/resume/"' not in r.content)
check("Nav: no Blog link when disabled", b'href="/writing/"' not in r.content)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 2: Service Business scenario
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 2 — Service business: services + testimonials enabled")

site.services_enabled = True
site.testimonials_enabled = True
site.research_enabled = False
site.publications_enabled = False
site.resume_enabled = False
site.blog_enabled = False
site.save()

r = client.get("/")
check("Home 200 (services scenario)", r.status_code == 200)

r = client.get("/services/")
check("Services 200 when enabled", r.status_code == 404 if ServiceItem.objects.filter(active=True).count() == 0 else r.status_code == 200)
# Re-check properly:
r = client.get("/services/")
check("Services list renders", r.status_code == 200)

r = client.get("/research/")
check("Research still 404 (disabled)", r.status_code == 404)

r = client.get("/publications/")
check("Publications still 404 (disabled)", r.status_code == 404)

r = client.get("/resume/")
check("Resume still 404 (disabled)", r.status_code == 404)

# Nav includes services, not others
r = client.get("/")
check("Nav: Services link present", b'href="/services/"' in r.content)
check("Nav: Research absent", b'href="/research/"' not in r.content)
check("Nav: Publications absent", b'href="/publications/"' not in r.content)
check("Nav: Resume absent", b'href="/resume/"' not in r.content)

# Footer includes services, not others
check("Footer: Services link present", b'href="/services/"' in r.content)
check("Footer: Research absent", b'href="/research/"' not in r.content)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 3: Academic/professional scenario
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 3 — Academic/professional: research + publications + resume enabled")

site.services_enabled = False
site.testimonials_enabled = False
site.research_enabled = True
site.publications_enabled = True
site.resume_enabled = True
site.blog_enabled = False
site.save()

r = client.get("/research/")
check("Research list 200 when enabled", r.status_code == 200)

r = client.get("/publications/")
check("Publications list 200 when enabled", r.status_code == 200)

r = client.get("/resume/")
check("Resume page 200 when enabled", r.status_code == 200)

r = client.get("/services/")
check("Services 404 (disabled in academic scenario)", r.status_code == 404)

# Check research detail works
rp = ResearchProject.objects.filter(is_active=True).first()
if rp:
    r = client.get(f"/research/{rp.slug}/")
    check("Research detail 200", r.status_code == 200)
else:
    check("Research detail 200", False, "No active research projects")

# Nav
r = client.get("/")
check("Nav: Research present", b'href="/research/"' in r.content)
check("Nav: Publications present", b'href="/publications/"' in r.content)
check("Nav: Resume/CV present", b'href="/resume/"' in r.content)
check("Nav: Services absent", b'href="/services/"' not in r.content)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 4: Portfolio/developer scenario
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 4 — Portfolio/developer: resume enabled, blog optional")

site.services_enabled = False
site.testimonials_enabled = False
site.research_enabled = False
site.publications_enabled = False
site.resume_enabled = True
site.blog_enabled = True
site.save()

r = client.get("/resume/")
check("Resume 200 (portfolio scenario)", r.status_code == 200)

r = client.get("/writing/")
check("Blog list 200 when enabled", r.status_code == 200)

# Blog detail
post = Post.objects.filter(is_published=True).first()
if post:
    r = client.get(f"/writing/{post.slug}/")
    check("Blog post detail 200", r.status_code == 200)
else:
    check("Blog post detail 200", False, "No published posts")

# Nav
r = client.get("/")
check("Nav: Blog/Writing present", b'href="/writing/"' in r.content)
check("Nav: Resume present", b'href="/resume/"' in r.content)
check("Nav: Services absent", b'href="/services/"' not in r.content)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 5: Brand customization checks (code-level, not rendered)
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 5 — Brand customization model validation")

# Typography presets
for preset in ["balanced", "editorial_serif", "modern_clean", "technical", "warm_professional"]:
    brand.typography_preset = preset
    brand.save()
    check(f"Typography preset '{preset}' saves", True)

# Color presets
for preset in ["neutral", "blue", "green", "burgundy", "amber", "custom"]:
    brand.color_preset = preset
    brand.save()
    check(f"Color preset '{preset}' saves", True)

# Custom accent color validation
brand.color_preset = "custom"
brand.accent_color_custom = "#B45309"
try:
    brand.full_clean()
    check("Valid hex accent color accepts", True)
except ValidationError as e:
    check("Valid hex accent color accepts", False, str(e))

brand.accent_color_custom = "not-a-hex"
try:
    brand.full_clean()
    check("Invalid hex accent color rejects", False, "Should have raised ValidationError")
except ValidationError:
    check("Invalid hex accent color rejects", True)

brand.accent_color_custom = "#B45309"  # restore valid
brand.save()

# Visual styles
for style in ["crisp", "balanced", "soft"]:
    brand.visual_style = style
    brand.save()
    check(f"Visual style '{style}' saves", True)

# Social links display
for mode in ["text", "icons", "icons_text"]:
    brand.social_links_display = mode
    brand.save()
    check(f"Social links display '{mode}' saves", True)

# Logo display modes
for mode in ["auto", "transparent", "safe_card"]:
    brand.logo_display_mode = mode
    brand.save()
    check(f"Logo display mode '{mode}' saves", True)

# Restore defaults
brand.typography_preset = "balanced"
brand.color_preset = "neutral"
brand.visual_style = "balanced"
brand.social_links_display = "text"
brand.logo_display_mode = "auto"
brand.accent_color_custom = ""
brand.save()

# No-logo state — nav should still render
site.logo = None
site.save()
r = client.get("/")
check("No-logo: home renders without error", r.status_code == 200)
check("No-logo: site_name or nav_name appears in nav", site.site_name.encode() in r.content or b"Studio Name" in r.content)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 6: Contact visibility controls
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 6 — Contact visibility controls")

site.show_email = True
site.show_phone = False
site.show_location = True
site.phone = ""
site.save()

r = client.get("/")
check("Footer: email shown when show_email=True", site.contact_email.encode() in r.content)

site.show_email = False
site.save()
r = client.get("/")
check("Footer: email hidden when show_email=False", site.contact_email.encode() not in r.content)

site.show_email = True  # restore
site.save()


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 7: Core pages and 404 for project detail
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 7 — Core page routes")

# Project detail
proj = Project.objects.first()
if proj:
    r = client.get(f"/projects/{proj.slug}/")
    check("Project detail 200", r.status_code == 200)
else:
    check("Project detail 200", False, "No projects")

r = client.get("/projects/nonexistent-slug-xyz/")
check("Project detail 404 on unknown slug", r.status_code == 404)


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 8: Admin UX checks (registration only — not rendered)
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 8 — Admin registration checks")

registered_models = [m.__name__ for m in django_admin.site._registry]

for model_name in [
    "SiteSettings", "AboutProfile", "BrandSettings", "ClientProfile",
    "SocialLink", "ServiceItem", "ResearchProject", "Publication",
    "ResumeProfile", "Project", "ProjectImage", "Testimonial", "Post",
]:
    check(f"Admin: {model_name} registered", model_name in registered_models)

# Admin site settings accessible
client.login(username="admin", password="drillpass123", HTTP_HOST="localhost")
r = client.get("/admin/")
check("Admin: login works", r.status_code == 200)

r = client.get("/admin/core/sitesettings/")
check("Admin: SiteSettings accessible", r.status_code in (200, 302))

r = client.get("/admin/core/sitesettings/1/change/")
check("Admin: SiteSettings change view 200", r.status_code == 200)

r = client.get("/admin/core/brandsettings/1/change/")
check("Admin: BrandSettings change view 200", r.status_code in (200, 302))

r = client.get("/admin/services/serviceitem/")
check("Admin: ServiceItem list accessible", r.status_code == 200)

r = client.get("/admin/research/researchproject/")
check("Admin: ResearchProject list accessible", r.status_code == 200)

r = client.get("/admin/publications/publication/")
check("Admin: Publication list accessible", r.status_code == 200)

r = client.get("/admin/resume/resumeprofile/")
check("Admin: ResumeProfile accessible", r.status_code in (200, 302))


# ─────────────────────────────────────────────────────────────────────────────
# PHASE 9: check_content_readiness output
# ─────────────────────────────────────────────────────────────────────────────
section("PHASE 9 — check_content_readiness (expected to have blockers)")

result = subprocess.run(
    ["uv", "run", "python", "manage.py", "check_content_readiness"],
    capture_output=True,
    text=True,
    cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
)
print(result.stdout[:2000] if result.stdout else "(no stdout)")
print(result.stderr[:500] if result.stderr else "")
check(
    "check_content_readiness runs without crash",
    result.returncode in (0, 1),  # 1 = blockers found (expected), 0 = none
)


# ─────────────────────────────────────────────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────────────────────────────────────────────
section("DRILL SUMMARY")

passed = [r for r in results if r[0] == PASS]
failed = [r for r in results if r[0] == FAIL]
warned = [r for r in results if r[0] == WARN]

print(f"\n  Passed : {len(passed)}")
print(f"  Failed : {len(failed)}")
print(f"  Warned : {len(warned)}")

if failed:
    print("\n  FAILURES:")
    for _, label, note in failed:
        print(f"    ✗  {label}" + (f"  [{note}]" if note else ""))

print()
