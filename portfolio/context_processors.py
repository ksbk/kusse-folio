from .models import SiteSettings


def site_settings(request):
    """Make SiteSettings available in every template as `settings`."""
    return {"site_settings": SiteSettings.load()}
