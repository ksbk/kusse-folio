"""
View tests for apps.resume: resume/CV page.
"""

import pytest
from django.urls import reverse

from apps.resume.models import ResumeProfile
from apps.site.models import SiteSettings

# ---------------------------------------------------------------------------
# Guard: resume_enabled = False → 404
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_resume_page_returns_404_when_disabled(client):
    site = SiteSettings.objects.get_or_create(pk=1, defaults={"site_name": "Test Site"})[0]
    site.resume_enabled = False
    site.save()
    response = client.get(reverse("resume:page"))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Guard: resume_enabled = True → 200
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_resume_page_returns_200_when_enabled(client, site_settings):
    site_settings.resume_enabled = True
    site_settings.resume_meta_title = "Academic CV"
    site_settings.resume_meta_description = "Academic background and selected CV details."
    site_settings.save()
    response = client.get(reverse("resume:page"))
    assert response.status_code == 200
    assert b"<title>Academic CV" in response.content
    assert b'content="Academic background and selected CV details."' in response.content


# ---------------------------------------------------------------------------
# Content rendering
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_resume_page_shows_headline(client, site_settings):
    site_settings.resume_enabled = True
    site_settings.save()
    profile, _ = ResumeProfile.objects.get_or_create(pk=1)
    profile.headline = "Researcher and Educator"
    profile.is_active = True
    profile.save()
    response = client.get(reverse("resume:page"))
    assert b"Researcher and Educator" in response.content


@pytest.mark.django_db
def test_resume_page_shows_summary(client, site_settings):
    site_settings.resume_enabled = True
    site_settings.save()
    profile, _ = ResumeProfile.objects.get_or_create(pk=1)
    profile.summary = "A distinguished career in design research."
    profile.is_active = True
    profile.save()
    response = client.get(reverse("resume:page"))
    assert b"A distinguished career in design research." in response.content


@pytest.mark.django_db
def test_resume_page_hides_download_when_no_file(client, site_settings):
    """No cv_file: download button must not appear."""
    site_settings.resume_enabled = True
    site_settings.save()
    profile, _ = ResumeProfile.objects.get_or_create(pk=1)
    profile.cv_file = None
    profile.is_active = True
    profile.save()
    response = client.get(reverse("resume:page"))
    assert b"Download CV" not in response.content


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_resume_page_context_has_resume(client, site_settings):
    site_settings.resume_enabled = True
    site_settings.save()
    response = client.get(reverse("resume:page"))
    assert "resume" in response.context
    assert isinstance(response.context["resume"], ResumeProfile)
