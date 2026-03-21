"""
View tests for apps.pages: home and about pages.
"""

import pytest
from django.urls import reverse


@pytest.mark.django_db
def test_home_page(client, site_settings):
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_about_page(client, site_settings):
    response = client.get(reverse("pages:about"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_home_all_projects_excludes_featured(client, site_settings, project):
    """Featured projects should not appear in 'all_projects' context."""
    project.featured = True
    project.save()
    response = client.get(reverse("pages:home"))
    assert response.status_code == 200
    all_pks = [p.pk for p in response.context["all_projects"]]
    assert project.pk not in all_pks
