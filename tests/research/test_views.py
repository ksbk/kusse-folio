"""
View tests for apps.research: research list and detail.
"""

import pytest
from django.urls import reverse

from apps.research.models import ResearchProject
from apps.site.models import SiteSettings


def _project(**kwargs) -> ResearchProject:
    defaults = {
        "title": "Test Research Project",
        "summary": "A brief summary.",
        "status": "ongoing",
        "is_active": True,
        "is_featured": False,
        "order": 1,
    }
    defaults.update(kwargs)
    return ResearchProject.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Guard: research_enabled = False → 404
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_research_list_returns_404_when_disabled(client):
    site = SiteSettings.objects.get_or_create(pk=1, defaults={"site_name": "Test Site"})[0]
    site.research_enabled = False
    site.save()
    response = client.get(reverse("research:list"))
    assert response.status_code == 404


@pytest.mark.django_db
def test_research_detail_returns_404_when_disabled(client):
    site = SiteSettings.objects.get_or_create(pk=1, defaults={"site_name": "Test Site"})[0]
    site.research_enabled = False
    site.save()
    p = _project(title="Detail Test")
    response = client.get(reverse("research:detail", kwargs={"slug": p.slug}))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Guard: research_enabled = True → 200
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_research_list_returns_200_when_enabled(client, site_settings):
    site_settings.research_enabled = True
    site_settings.save()
    response = client.get(reverse("research:list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_research_detail_returns_200_when_enabled(client, site_settings):
    site_settings.research_enabled = True
    site_settings.save()
    p = _project(title="Active Detail Project")
    response = client.get(reverse("research:detail", kwargs={"slug": p.slug}))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Content rendering
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_research_list_shows_active_project(client, site_settings):
    site_settings.research_enabled = True
    site_settings.save()
    _project(title="Visible Research")
    response = client.get(reverse("research:list"))
    assert b"Visible Research" in response.content


@pytest.mark.django_db
def test_research_list_excludes_inactive_project(client, site_settings):
    site_settings.research_enabled = True
    site_settings.save()
    _project(title="Hidden Research", is_active=False)
    response = client.get(reverse("research:list"))
    assert b"Hidden Research" not in response.content


@pytest.mark.django_db
def test_research_detail_shows_inactive_project_as_404(client, site_settings):
    """Inactive projects should not be accessible via their detail URL."""
    site_settings.research_enabled = True
    site_settings.save()
    p = _project(title="Inactive Detail", is_active=False)
    response = client.get(reverse("research:detail", kwargs={"slug": p.slug}))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_research_list_context_has_research_projects(client, site_settings):
    site_settings.research_enabled = True
    site_settings.save()
    _project(title="Context Project")
    response = client.get(reverse("research:list"))
    assert "research_projects" in response.context
    titles = [p.title for p in response.context["research_projects"]]
    assert "Context Project" in titles
