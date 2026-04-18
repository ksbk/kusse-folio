"""
Tests for check_content_readiness management command.

Tests call collect_warnings() directly to avoid sys.exit() in tests.
Each test runs against a fresh isolated DB (pytest-django default).
"""

import pytest
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings

from apps.projects.models import Project, Testimonial
from apps.site.about_defaults import (
    CLOSING_INVITATION_DEFAULT,
    PRACTICE_STRUCTURE_PROMPT,
    PROFESSIONAL_STANDING_PROMPT,
    PROJECT_LEADERSHIP_PROMPT,
)
from apps.site.management.commands.check_content_readiness import (
    collect_readiness_issues,
    collect_warnings,
)
from apps.site.management.commands.seed_demo import _discover_demo_media_dir
from apps.site.models import AboutProfile, SiteSettings

# ---------------------------------------------------------------------------
# SiteSettings checks
# ---------------------------------------------------------------------------


def _populate_minimum_ready_site_and_about():
    site = SiteSettings.load()
    site.site_name = "Studio Rossi"
    site.contact_email = "studio@mypractice.com"
    site.tagline = "Context-led design"
    site.meta_description = "Independent creative studio."
    site.location = "Reykjavik, Iceland"
    site.og_image = SimpleUploadedFile("og.jpg", b"og-image", content_type="image/jpeg")
    site.save()

    about = AboutProfile.load()
    about.identity_mode = AboutProfile.IdentityMode.STUDIO
    about.professional_context = "Small studio"
    about.one_line_bio = "Design for spatial and visual projects."
    about.bio_summary = "A studio working across public and private projects."
    about.work_approach = (
        "Projects are led directly with specialist collaborators involved as needed."
    )
    about.professional_standing = "Independent studio"
    about.education = "MA Design"
    about.supporting_facts = ""
    about.experience_years = 12
    about.approach = "The work focuses on clarity, durability, and legible project decision-making."
    about.closing_invitation = "Get in touch to discuss a project."
    about.portrait_mode = AboutProfile.PortraitMode.TEXT_ONLY
    about.save()
    return site, about


@pytest.mark.django_db
def test_warns_when_site_name_is_blank():
    # SiteSettings.load() on a fresh DB creates with site_name = "" (blank default).
    warnings = collect_warnings()
    assert any("site_name" in w for w in warnings)


@pytest.mark.django_db
def test_no_site_name_warning_when_customised():
    site = SiteSettings.load()
    site.site_name = "Priya Patel Architecture"
    site.save()
    warnings = collect_warnings()
    assert not any("site_name" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_contact_email_is_blank():
    # SiteSettings.load() creates with contact_email = "" (blank default).
    warnings = collect_warnings()
    assert any("contact_email" in w for w in warnings)


@pytest.mark.django_db
def test_no_contact_email_warning_when_customised():
    site = SiteSettings.load()
    site.contact_email = "studio@mypractice.com"
    site.save()
    warnings = collect_warnings()
    assert not any("contact_email" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_site_name_is_still_demo_value():
    site = SiteSettings.load()
    site.site_name = "Demo Portfolio Studio"
    site.contact_email = "studio@mypractice.com"
    site.save()
    warnings = collect_warnings()
    assert any("starter value ('Demo Portfolio Studio')" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_contact_email_is_still_demo_value():
    site = SiteSettings.load()
    site.site_name = "Studio Rossi"
    site.contact_email = "hello@demo-portfolio.example"
    site.save()
    warnings = collect_warnings()
    assert any("hello@demo-portfolio.example" in w for w in warnings)


# ---------------------------------------------------------------------------
# AboutProfile checks
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_warns_when_experience_years_is_zero():
    # AboutProfile.load() on a fresh DB has experience_years=0 (model default).
    warnings = collect_warnings()
    assert any("experience_years" in w for w in warnings)


@pytest.mark.django_db
def test_no_experience_years_warning_when_set():
    about = AboutProfile.load()
    about.experience_years = 12
    about.save()
    warnings = collect_warnings()
    assert not any("experience_years" in w for w in warnings)


@pytest.mark.django_db
def test_warns_when_about_contains_placeholder_markers():
    site = SiteSettings.load()
    site.site_name = "Studio Rossi"
    site.contact_email = "studio@mypractice.com"
    site.save()

    about = AboutProfile.load()
    about.professional_context = "Small studio"
    about.one_line_bio = "[Add a one-line public description of yourself]"
    about.save()

    warnings = collect_warnings()
    assert any("starter placeholder markers" in w for w in warnings)


@pytest.mark.django_db
def test_about_readiness_warns_but_does_not_block_in_text_only_mode(project):
    _populate_minimum_ready_site_and_about()

    blockers, warnings = collect_readiness_issues()

    assert not any("AboutProfile" in blocker for blocker in blockers)
    assert any("text-only mode" in warning for warning in warnings)


@pytest.mark.django_db
def test_readiness_warns_when_page_specific_meta_descriptions_are_blank(project):
    _populate_minimum_ready_site_and_about()

    blockers, warnings = collect_readiness_issues()

    assert not any("meta_description is blank" in blocker for blocker in blockers)
    assert any("about_meta_description is blank" in warning for warning in warnings)
    assert any("projects_meta_description is blank" in warning for warning in warnings)
    assert any("contact_meta_description is blank" in warning for warning in warnings)


@pytest.mark.django_db
def test_readiness_blocks_when_nonblank_page_meta_references_a_different_studio_identity(
    project
):
    site, _ = _populate_minimum_ready_site_and_about()
    site.about_meta_description = "About Demo Portfolio Studio, the studio approach, experience, and professional profile."
    site.save()

    blockers, warnings = collect_readiness_issues()

    assert any("about_meta_description still references 'Demo Portfolio Studio'" in blocker for blocker in blockers)
    assert not any("about_meta_description is blank" in warning for warning in warnings)


@pytest.mark.django_db
def test_readiness_warns_when_custom_og_image_is_missing_but_no_longer_blocks(project):
    site, _ = _populate_minimum_ready_site_and_about()
    site.og_image.delete(save=True)

    blockers, warnings = collect_readiness_issues()

    assert not any("SiteSettings.og_image is missing" in blocker for blocker in blockers)
    assert any("SiteSettings.og_image is missing" in warning for warning in warnings)


@pytest.mark.django_db
def test_seed_about_sets_safe_default_invitation_and_truth_prompts():
    about = AboutProfile.load()

    call_command("seed_about")
    about.refresh_from_db()

    assert about.professional_context == PRACTICE_STRUCTURE_PROMPT
    assert about.work_approach == PROJECT_LEADERSHIP_PROMPT
    assert about.professional_standing == PROFESSIONAL_STANDING_PROMPT
    assert about.closing_invitation == CLOSING_INVITATION_DEFAULT


@pytest.mark.django_db
def test_about_readiness_warns_when_truth_fields_are_omitted_or_starter_prompts(project):
    _, about = _populate_minimum_ready_site_and_about()
    about.professional_context = PRACTICE_STRUCTURE_PROMPT
    about.work_approach = ""
    about.professional_standing = PROFESSIONAL_STANDING_PROMPT
    about.save()

    blockers, warnings = collect_readiness_issues()

    assert not any("professional_context" in blocker for blocker in blockers)
    assert not any("work_approach" in blocker for blocker in blockers)
    assert not any("professional_standing" in blocker for blocker in blockers)
    assert any("professional_context is omitted or still a starter prompt" in warning for warning in warnings)
    assert any("work_approach is omitted or still a starter prompt" in warning for warning in warnings)
    assert any("professional_standing is omitted or still a starter prompt" in warning for warning in warnings)


@pytest.mark.django_db
def test_about_readiness_blocks_when_person_led_name_is_missing(project):
    _, about = _populate_minimum_ready_site_and_about()
    about.identity_mode = AboutProfile.IdentityMode.PERSON
    about.principal_title = "Founder and Registered Architect"
    about.save()

    blockers, _ = collect_readiness_issues()

    assert any("principal_name" in blocker for blocker in blockers)


@pytest.mark.django_db
def test_about_readiness_blocks_when_minimum_profile_fact_set_is_missing(project):
    _, about = _populate_minimum_ready_site_and_about()
    about.education = ""
    about.supporting_facts = ""
    about.save()

    blockers, _ = collect_readiness_issues()

    assert any("concrete supporting fact" in blocker for blocker in blockers)


@pytest.mark.django_db
def test_about_readiness_blocks_when_optional_proof_fields_contain_only_starter_prompts(project):
    _, about = _populate_minimum_ready_site_and_about()
    about.education = "[Add education details, one per line]"
    about.supporting_facts = "[Add at least one concrete supporting fact, one per line]"
    about.save()

    blockers, _ = collect_readiness_issues()

    assert any("concrete supporting fact" in blocker for blocker in blockers)


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("field", "value", "expected_message"),
    [
        (
            "professional_context",
            PRACTICE_STRUCTURE_PROMPT,
            "AboutProfile.professional_context is omitted or still a starter prompt.",
        ),
        (
            "work_approach",
            PROJECT_LEADERSHIP_PROMPT,
            "AboutProfile.work_approach is omitted or still a starter prompt.",
        ),
        (
            "professional_standing",
            PROFESSIONAL_STANDING_PROMPT,
            "AboutProfile.professional_standing is omitted or still a starter prompt.",
        ),
    ],
)
def test_about_readiness_warns_when_truth_fields_are_still_starter_prompts(
    project,
    field,
    value,
    expected_message,
):
    _, about = _populate_minimum_ready_site_and_about()
    setattr(about, field, value)
    about.closing_invitation = CLOSING_INVITATION_DEFAULT
    about.save()

    blockers, warnings = collect_readiness_issues()

    assert not any(field in blocker for blocker in blockers)
    assert any(expected_message in warning for warning in warnings)
    assert not any("closing_invitation is blank" in blocker for blocker in blockers)


@pytest.mark.django_db
def test_about_readiness_does_not_add_generic_placeholder_blocker_for_optional_proof_prompts(
    project
):
    _, about = _populate_minimum_ready_site_and_about()
    about.education = "[Add education details, one per line]"
    about.closing_invitation = CLOSING_INVITATION_DEFAULT
    about.save()

    blockers, _ = collect_readiness_issues()

    assert not any("starter placeholder markers" in blocker for blocker in blockers)


# ---------------------------------------------------------------------------
# Content collection checks
# ---------------------------------------------------------------------------


@pytest.mark.django_db
@override_settings(CONTACT_EMAIL="")
def test_readiness_warns_when_internal_contact_inbox_is_missing(project):
    _populate_minimum_ready_site_and_about()

    _, warnings = collect_readiness_issues()

    assert any("CONTACT_EMAIL is blank" in warning for warning in warnings)


@pytest.mark.django_db
def test_readiness_warns_when_no_featured_projects_are_selected(project):
    _populate_minimum_ready_site_and_about()
    Project.objects.update(featured=False)

    _, warnings = collect_readiness_issues()

    assert any("No featured Project records are selected" in warning for warning in warnings)


@pytest.mark.django_db
def test_readiness_warns_when_homepage_hero_project_has_no_cover_image():
    _populate_minimum_ready_site_and_about()
    Project.objects.create(
        title="Featured Without Cover",
        slug="featured-without-cover",
        short_description=".",
        tags="housing",
        status="completed",
        featured=True,
        order=1,
    )

    blockers, warnings = collect_readiness_issues()

    assert not blockers
    assert any("homepage hero project ('Featured Without Cover') has no cover image" in warning for warning in warnings)


def test_seed_demo_auto_discovers_tracked_bundled_media(tmp_path):
    bundled = _discover_demo_media_dir(tmp_path)

    assert bundled is not None
    assert bundled.name == "strand-architecture"
    assert (bundled / "covers").is_dir()
    assert (bundled / "gallery").is_dir()


@pytest.mark.django_db
def test_seed_demo_populates_signed_off_project_preview_states_from_tracked_bundle(settings, tmp_path):
    settings.MEDIA_ROOT = tmp_path

    call_command("seed_demo")

    expected_cover_slugs = [
        "community-library-pavilion",
        "commercial-office-conversion",
        "civic-waterfront-square",
        "housing-block-north-quarter",
        "school-extension-timber-frame",
        "urban-apartment-retrofit",
    ]
    for slug in expected_cover_slugs:
        project = Project.objects.get(slug=slug)
        assert project.cover_image

    assert Project.objects.get(slug="coastline-civic-centre").images.count() == 4
    assert Project.objects.get(slug="harbour-court-apartments").images.count() == 5
    assert Project.objects.get(slug="ridgeline-housing").images.count() == 7


@pytest.mark.django_db
def test_seed_demo_sets_coherent_about_demo_defaults_without_forcing_non_portrait_image_publicly():
    call_command("seed_demo")

    site = SiteSettings.load()
    about = AboutProfile.load()

    assert site.location == "Your City, Your Country"
    assert site.about_meta_description == (
        "About Demo Portfolio Studio, the studio approach, experience, and professional profile."
    )
    assert about.portrait_mode == AboutProfile.PortraitMode.TEXT_ONLY


@pytest.mark.django_db
def test_readiness_blocks_when_demo_projects_remain():
    _populate_minimum_ready_site_and_about()
    Project.objects.create(
        title="House on the Hillside",
        slug="house-on-the-hillside",
        short_description=".",
        tags="housing",
        status="completed",
    )

    blockers, _ = collect_readiness_issues()

    assert any("Starter Project records are still present" in blocker for blocker in blockers)


@pytest.mark.django_db
def test_readiness_blocks_when_demo_testimonials_remain(project):
    _populate_minimum_ready_site_and_about()
    Testimonial.objects.create(
        project=project,
        name="A. Navarro",
        quote="Excellent.",
        order=1,
        active=True,
    )

    blockers, _ = collect_readiness_issues()

    assert any("Starter Testimonial records are still present" in blocker for blocker in blockers)
