"""
View tests for apps.services: services list.
"""

import pytest
from django.urls import reverse

from apps.services.models import ServiceItem
from apps.site.models import SiteSettings


def _service(**kwargs) -> ServiceItem:
    defaults = {
        "name": "Design Consulting",
        "short_description": "We help you design better things.",
        "order": 1,
        "active": True,
    }
    defaults.update(kwargs)
    return ServiceItem.objects.create(**defaults)


# ---------------------------------------------------------------------------
# Enabled guard
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_services_list_returns_404_when_disabled(client):
    site = SiteSettings.objects.get_or_create(pk=1, defaults={"site_name": "Test Site"})[0]
    site.services_enabled = False
    site.save()
    response = client.get(reverse("services:list"))
    assert response.status_code == 404


@pytest.mark.django_db
def test_services_list_returns_200_when_enabled(client, site_settings):
    site_settings.services_enabled = True
    site_settings.services_meta_title = "Advisory Services"
    site_settings.services_meta_description = "Consulting and advisory services."
    site_settings.save()
    response = client.get(reverse("services:list"))
    assert response.status_code == 200
    assert b"<title>Advisory Services" in response.content
    assert b'content="Consulting and advisory services."' in response.content


# ---------------------------------------------------------------------------
# Content rendering
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_services_list_shows_active_service(client, site_settings):
    site_settings.services_enabled = True
    site_settings.save()
    _service(name="Brand Strategy", short_description="We shape how you're seen.")
    response = client.get(reverse("services:list"))
    assert b"Brand Strategy" in response.content
    assert b"We shape how you&#x27;re seen." in response.content or b"We shape how you're seen." in response.content


@pytest.mark.django_db
def test_services_list_excludes_inactive_service(client, site_settings):
    site_settings.services_enabled = True
    site_settings.save()
    _service(name="Hidden Service", active=False)
    response = client.get(reverse("services:list"))
    assert b"Hidden Service" not in response.content


@pytest.mark.django_db
def test_services_list_respects_order(client, site_settings):
    site_settings.services_enabled = True
    site_settings.save()
    _service(name="Last Item", order=99)
    _service(name="First Item", order=1)
    response = client.get(reverse("services:list"))
    html = response.content.decode()
    first_pos = html.find("First Item")
    last_pos = html.find("Last Item")
    assert first_pos < last_pos, "Active services should render in 'order' field sequence"


@pytest.mark.django_db
def test_services_list_shows_empty_state(client, site_settings):
    site_settings.services_enabled = True
    site_settings.save()
    # No services seeded — page should still render without error
    response = client.get(reverse("services:list"))
    assert response.status_code == 200


# ---------------------------------------------------------------------------
# Context
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_services_list_context_has_services_queryset(client, site_settings):
    site_settings.services_enabled = True
    site_settings.save()
    _service(name="Context Service")
    response = client.get(reverse("services:list"))
    assert "services" in response.context
    names = [s.name for s in response.context["services"]]
    assert "Context Service" in names
