"""
Contact form tests — valid POST creates a ContactInquiry; invalid POST stays on page.
"""

import pytest
from django.urls import reverse

from portfolio.models import ContactInquiry

VALID_PAYLOAD = {
    "name": "Alice Architect",
    "email": "alice@example.com",
    "message": "I would like to discuss a residential project.",
    "project_type": "Residential Design",
    "budget_range": "R2M – R5M",
    "timeline": "3–6 months",
}


@pytest.mark.django_db
def test_contact_form_valid_post_creates_inquiry(client, site_settings):
    assert ContactInquiry.objects.count() == 0
    response = client.post(reverse("contact"), data=VALID_PAYLOAD, follow=False)
    # Should redirect to the thank-you page
    assert response.status_code == 302
    assert response["Location"] == reverse("contact_success")
    assert ContactInquiry.objects.count() == 1

    inquiry = ContactInquiry.objects.get(email="alice@example.com")
    assert inquiry.name == "Alice Architect"
    assert inquiry.email == "alice@example.com"
    assert inquiry.status == "new"


@pytest.mark.django_db
def test_contact_form_missing_required_fields_stays_on_page(client, site_settings):
    response = client.post(reverse("contact"), data={"name": "", "email": "", "message": ""})
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_contact_form_invalid_email(client, site_settings):
    payload = {**VALID_PAYLOAD, "email": "not-an-email"}
    response = client.post(reverse("contact"), data=payload)
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_honeypot_filled_rejects_submission(client, site_settings):
    """A submission with the honeypot field filled should be silently rejected."""
    payload = {**VALID_PAYLOAD, "website": "http://spam.example.com"}
    response = client.post(reverse("contact"), data=payload)
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0


@pytest.mark.django_db
def test_short_message_rejected(client, site_settings):
    """Messages shorter than 20 characters should fail validation."""
    payload = {**VALID_PAYLOAD, "message": "Too short."}
    response = client.post(reverse("contact"), data=payload)
    assert response.status_code == 200
    assert ContactInquiry.objects.count() == 0
