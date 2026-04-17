from apps.site.models import SiteSettings, SocialLink


def site_settings(request):
    """Make SiteSettings and SocialLink entries available in every template."""
    return {
        "site_settings": SiteSettings.load(),
        "social_links": list(SocialLink.objects.filter(active=True).order_by("order", "label")),
    }
