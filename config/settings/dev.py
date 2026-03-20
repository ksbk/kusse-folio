"""
Development settings.

Activate with:
    DJANGO_SETTINGS_MODULE=config.settings.dev
This is the default set by manage.py for local work.
"""

from .base import *  # noqa: F401, F403

DEBUG = True

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0"]  # noqa: S104

# Show Django debug toolbar or similar tools here if added later.
# Email goes to the console so no SMTP config is needed locally.
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Relaxed security in local dev — cookies don't need HTTPS
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
