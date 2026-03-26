"""
Model tests for apps.services: Service.
"""

import pytest

from apps.services.models import Service


@pytest.mark.django_db
def test_service_str(service):
    assert str(service) == "Architectural Design"


@pytest.mark.django_db
def test_service_slug_auto_generated():
    s = Service.objects.create(title="Urban Planning", order=10, active=True)
    assert s.slug == "urban-planning"


@pytest.mark.django_db
def test_service_deliverables_list(db):
    s = Service.objects.create(
        title="Test Service",
        order=1,
        active=True,
        deliverables="Item one\nItem two\nItem three",
    )
    items = s.deliverables_list()
    assert len(items) == 3
    assert "Item one" in items


@pytest.mark.django_db
def test_service_contact_project_type_mapping():
    housing = Service.objects.create(
        title="Housing",
        slug="housing",
        summary="Housing projects.",
        order=1,
        active=True,
    )
    civic = Service.objects.create(
        title="Civic",
        slug="civic-community-buildings",
        summary="Public-facing building work.",
        order=2,
        active=True,
    )
    workplace = Service.objects.create(
        title="Workplace",
        slug="workplace",
        summary="Workplace projects.",
        order=3,
        active=True,
    )

    assert housing.contact_project_type == "Housing"
    assert civic.contact_project_type == "Civic"
    assert workplace.contact_project_type == "Workplace"
