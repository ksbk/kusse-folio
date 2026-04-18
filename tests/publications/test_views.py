"""
View tests for apps.publications: publications list.
"""

import pytest
from django.urls import reverse

from apps.publications.models import Publication
from apps.site.models import SiteSettings


def _publication(**kwargs) -> Publication:
    defaults = {
        "title": "Test Publication",
        "authors": "Author, A.",
        "venue": "Test Journal",
        "year": 2023,
        "is_active": True,
        "is_featured": False,
        "order": 1,
    }
    defaults.update(kwargs)
    return Publication.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Guard: publications_enabled = False → 404
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_publications_list_returns_404_when_disabled(client):
    site = SiteSettings.objects.get_or_create(pk=1, defaults={"site_name": "Test Site"})[0]
    site.publications_enabled = False
    site.save()
    response = client.get(reverse("publications:list"))
    assert response.status_code == 404


# ---------------------------------------------------------------------------
# Guard: publications_enabled = True → 200
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_publications_list_returns_200_when_enabled(client, site_settings):
    site_settings.publications_enabled = True
    site_settings.save()
    response = client.get(reverse("publications:list"))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Content rendering
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_publications_list_shows_active_publication(client, site_settings):
    site_settings.publications_enabled = True
    site_settings.save()
    _publication(title="Visible Publication")
    response = client.get(reverse("publications:list"))
    assert b"Visible Publication" in response.content


@pytest.mark.django_db
def test_publications_list_excludes_inactive_publication(client, site_settings):
    site_settings.publications_enabled = True
    site_settings.save()
    _publication(title="Hidden Publication", is_active=False)
    response = client.get(reverse("publications:list"))
    assert b"Hidden Publication" not in response.content


@pytest.mark.django_db
def test_publications_list_shows_empty_state_without_error(client, site_settings):
    site_settings.publications_enabled = True
    site_settings.save()
    response = client.get(reverse("publications:list"))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_publications_list_context_has_publications(client, site_settings):
    site_settings.publications_enabled = True
    site_settings.save()
    _publication(title="Context Publication")
    response = client.get(reverse("publications:list"))
    assert "publications" in response.context
    titles = [p.title for p in response.context["publications"]]
    assert "Context Publication" in titles
