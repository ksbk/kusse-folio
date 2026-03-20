"""
Tests for portfolio/checks.py — the Django system check that guards against
a dev-only email backend being active in production-like mode (DEBUG=False).
"""

from django.test import override_settings

from portfolio.checks import check_production_email_backend

_CONSOLE = "django.core.mail.backends.console.EmailBackend"
_DUMMY = "django.core.mail.backends.dummy.EmailBackend"
_LOCMEM = "django.core.mail.backends.locmem.EmailBackend"
_SMTP = "django.core.mail.backends.smtp.EmailBackend"


@override_settings(DEBUG=False, EMAIL_BACKEND=_CONSOLE)
def test_check_warns_when_debug_false_and_console_backend():
    """W001 fires when DEBUG=False and EMAIL_BACKEND is the console backend."""
    errors = check_production_email_backend(None)
    assert len(errors) == 1
    assert errors[0].id == "portfolio.W001"
    assert "DEBUG=False" in errors[0].msg
    assert _CONSOLE in errors[0].msg


@override_settings(DEBUG=False, EMAIL_BACKEND=_DUMMY)
def test_check_warns_for_dummy_backend():
    errors = check_production_email_backend(None)
    assert len(errors) == 1
    assert errors[0].id == "portfolio.W001"


@override_settings(DEBUG=False, EMAIL_BACKEND=_LOCMEM)
def test_check_warns_for_locmem_backend():
    errors = check_production_email_backend(None)
    assert len(errors) == 1
    assert errors[0].id == "portfolio.W001"


@override_settings(DEBUG=False, EMAIL_BACKEND=_SMTP)
def test_check_silent_when_debug_false_and_smtp_backend():
    """No warning when DEBUG=False and a real SMTP backend is configured."""
    errors = check_production_email_backend(None)
    assert errors == []


@override_settings(DEBUG=True, EMAIL_BACKEND=_CONSOLE)
def test_check_silent_when_debug_true():
    """No warning in development mode — console backend is expected there."""
    errors = check_production_email_backend(None)
    assert errors == []
