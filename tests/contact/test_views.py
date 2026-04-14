"""
View tests for apps.contact: contact page and success page.
"""

from unittest.mock import patch

import pytest
from django.test import override_settings
from django.urls import reverse


@pytest.mark.django_db
def test_contact_page_get(client, site_settings):
    site_settings.contact_email = "contact@example.com"
    site_settings.save()
    response = client.get(reverse("contact:contact"))
    assert response.status_code == 200
    assert b"The practice reviews each enquiry directly." in response.content
    assert b"Your details are used only to review and respond to your enquiry." in response.content
    assert b"For urgent matters, email directly." in response.content


@pytest.mark.django_db
def test_contact_page_renders_stable_describedby_targets_on_clean_get(client, site_settings):
    response = client.get(reverse("contact:contact"))

    assert response.status_code == 200
    assert b'aria-describedby="id_name_error"' in response.content
    assert b'id="id_name_error"' in response.content
    assert b'aria-describedby="id_email_error"' in response.content
    assert b'id="id_email_error"' in response.content
    assert b'aria-describedby="id_message_hint id_message_error"' in response.content
    assert b'id="id_message_hint"' in response.content
    assert b'id="id_message_error"' in response.content


@pytest.mark.django_db
def test_contact_success_page(client, site_settings):
    response = client.get(reverse("contact:success"))
    assert response.status_code == 200
    assert b"Your enquiry has been received." in response.content
    assert b"The practice usually replies within two working days." in response.content
    assert b"Next step" in response.content
    assert b"Explore Projects" in response.content
    assert b"Back to Home" in response.content


@pytest.mark.django_db
def test_contact_success_page_saved_only_state(client, site_settings):
    response = client.get(reverse("contact:success") + "?delivery=saved-only")

    assert response.status_code == 200
    assert b"Your enquiry has been received and saved." in response.content
    assert b"Email notification for the practice is currently unavailable" in response.content
    assert b"response time may be longer" in response.content


@pytest.mark.django_db
def test_contact_pages_use_configured_response_time_copy(client, site_settings):
    site_settings.contact_response_time = "one week"
    site_settings.save(update_fields=["contact_response_time"])

    contact = client.get(reverse("contact:contact"))
    success = client.get(reverse("contact:success"))

    assert b"Enquiries reviewed within one week" in contact.content
    assert b"The practice usually replies within one week." in success.content


@pytest.mark.django_db
def test_contact_prefills_project_type_from_query_param(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=Housing")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type") == "Housing"


@pytest.mark.django_db
def test_contact_maps_legacy_project_type_query_param(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=Residential+Design")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type") == "Housing"


@pytest.mark.django_db
def test_contact_maps_unsupported_legacy_project_type_query_param_to_other(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=Concept+Development")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type") == "Other"


@pytest.mark.django_db
def test_contact_ignores_invalid_project_type_query_param(client, site_settings):
    response = client.get(reverse("contact:contact") + "?project_type=MaliciousValue")
    assert response.status_code == 200
    form = response.context["form"]
    assert form.initial.get("project_type", "") == ""


# ---------------------------------------------------------------------------
# Contact form POST — email delivery path tests
# ---------------------------------------------------------------------------


def _get_post_data(client, site_settings):
    """Obtain a valid submission_token via GET, then build a minimal valid POST payload."""
    get_response = client.get(reverse("contact:contact"))
    token = get_response.context["form"].initial.get("submission_token", "")
    return {
        "name": "Test Buyer",
        "email": "buyer@example.com",
        "company": "",
        "project_type": "Housing",
        "location": "",
        "budget_range": "",
        "timeline": "",
        "message": "Interested in a housing project.",
        "website": "",  # honeypot — must be blank
        "submission_token": token,
    }


@pytest.mark.django_db
@override_settings(
    CONTACT_EMAIL="studio@example.com",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_FORM_MIN_AGE_SECONDS=0,
)
def test_contact_post_sends_email_and_redirects_to_sent(client, site_settings):
    """Happy path: valid POST with CONTACT_EMAIL set saves inquiry and sends notification."""
    from django.core import mail

    data = _get_post_data(client, site_settings)
    response = client.post(reverse("contact:contact"), data)

    assert response.status_code == 302
    assert "delivery=sent" in response["Location"]
    assert len(mail.outbox) == 1
    assert mail.outbox[0].to == ["studio@example.com"]


@pytest.mark.django_db
@override_settings(
    CONTACT_EMAIL="",
    EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend",
    CONTACT_FORM_MIN_AGE_SECONDS=0,
)
def test_contact_post_saved_only_when_contact_email_blank(client, site_settings):
    """Degraded path: blank CONTACT_EMAIL skips email and redirects to saved-only."""
    from django.core import mail

    data = _get_post_data(client, site_settings)
    response = client.post(reverse("contact:contact"), data)

    assert response.status_code == 302
    assert "delivery=saved-only" in response["Location"]
    assert len(mail.outbox) == 0  # no send attempt made


@pytest.mark.django_db
@override_settings(CONTACT_EMAIL="studio@example.com", CONTACT_FORM_MIN_AGE_SECONDS=0)
def test_contact_post_saved_only_when_email_send_raises(client, site_settings):
    """Degraded path: email send exception is caught and redirects to saved-only."""
    data = _get_post_data(client, site_settings)
    with patch("apps.contact.views.EmailMessage.send", side_effect=Exception("SMTP down")):
        response = client.post(reverse("contact:contact"), data)

    assert response.status_code == 302
    assert "delivery=saved-only" in response["Location"]
