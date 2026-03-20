"""
View sanity tests — every public route should return HTTP 200 for GET requests.
The contact form POST is tested separately in test_forms.py.
"""

import pytest
from django.urls import reverse

from portfolio.models import Testimonial

# ---------------------------------------------------------------------------
# Pages that need no database content to render (gracefully handle empty DB)
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_home_page(client, site_settings):
    response = client.get(reverse("home"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_page(client, site_settings):
    response = client.get(reverse("project_list"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_list_with_category_filter(client, site_settings, project):
    url = reverse("project_list") + "?category=residential"
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_page(client, site_settings, project):
    url = reverse("project_detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_project_detail_404_for_unknown_slug(client, site_settings):
    url = reverse("project_detail", kwargs={"slug": "does-not-exist"})
    response = client.get(url)
    assert response.status_code == 404


@pytest.mark.django_db
def test_about_page(client, site_settings):
    response = client.get(reverse("about"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_services_page(client, site_settings):
    response = client.get(reverse("services"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_page_get(client, site_settings):
    response = client.get(reverse("contact"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_contact_success_page(client, site_settings):
    response = client.get(reverse("contact_success"))
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_login_page_resolves(client):
    """Admin login should redirect or render — never 404/500."""
    response = client.get("/admin/login/")
    assert response.status_code in (200, 302)


# ---------------------------------------------------------------------------
# Project detail — context enrichments
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_project_detail_context_has_testimonials_key(client, site_settings, project):
    url = reverse("project_detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.status_code == 200
    assert "testimonials" in response.context


@pytest.mark.django_db
def test_project_detail_context_shows_linked_testimonials(client, site_settings, project):
    Testimonial.objects.create(
        name="Happy Client",
        quote="Exceptional design.",
        project=project,
        order=1,
        active=True,
    )
    url = reverse("project_detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.context["testimonials"].count() == 1


@pytest.mark.django_db
def test_project_detail_context_excludes_inactive_testimonials(client, site_settings, project):
    Testimonial.objects.create(
        name="Inactive Client",
        quote="Redacted.",
        project=project,
        order=1,
        active=False,
    )
    url = reverse("project_detail", kwargs={"slug": project.slug})
    response = client.get(url)
    assert response.context["testimonials"].count() == 0


# ---------------------------------------------------------------------------
# SEO routes
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_sitemap_returns_200(client, site_settings):
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"urlset" in response.content


@pytest.mark.django_db
def test_robots_txt_returns_200(client, site_settings):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"User-agent" in response.content
    assert b"sitemap.xml" in response.content


# ---------------------------------------------------------------------------
# Contact — project_type pre-fill from query param
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_contact_prefills_project_type_from_query_param(client, site_settings):
    response = client.get(reverse("contact") + "?project_type=Residential+Design")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type") == "Residential Design"


@pytest.mark.django_db
def test_contact_ignores_invalid_project_type_query_param(client, site_settings):
    response = client.get(reverse("contact") + "?project_type=MaliciousValue")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type", "") == ""


# ---------------------------------------------------------------------------
# Home — all_projects excludes featured
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_home_all_projects_excludes_featured(client, site_settings, project):
    """Featured projects should not appear in 'all_projects' context."""
    project.featured = True
    project.save()
    response = client.get(reverse("home"))
    assert response.status_code == 200
    all_pks = [p.pk for p in response.context["all_projects"]]
    assert project.pk not in all_pks
