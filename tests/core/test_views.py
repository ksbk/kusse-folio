"""
View tests for apps.core: admin, sitemap, robots.txt.
"""

import pytest


@pytest.mark.django_db
def test_admin_login_page_resolves(client):
    """Admin login should redirect or render — never 404/500."""
    response = client.get("/admin/login/")
    assert response.status_code in (200, 302)


@pytest.mark.django_db
def test_sitemap_returns_200(client, site_settings, project):
    """Sitemap renders with a project present so ProjectSitemap.lastmod/location are exercised."""
    response = client.get("/sitemap.xml")
    assert response.status_code == 200
    assert b"urlset" in response.content
    assert project.slug.encode() in response.content


@pytest.mark.django_db
def test_robots_txt_returns_200(client, site_settings):
    response = client.get("/robots.txt")
    assert response.status_code == 200
    assert b"User-agent" in response.content
    assert b"sitemap.xml" in response.content
