from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from apps.site.models import SiteSettings


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        items = [
            "pages:home",
            "projects:list",
            "pages:about",
            "contact:contact",
            "pages:website_service",
        ]
        if SiteSettings.load().blog_enabled:
            items.append("blog:list")
        return items

    def location(self, item: str) -> str:
        return reverse(item)
