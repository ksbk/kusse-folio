from django.contrib.sitemaps import Sitemap
from django.urls import reverse


class StaticViewSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return [
            "portfolio:home",
            "projects:list",
            "portfolio:about",
            "portfolio:services",
            "contact:contact",
        ]

    def location(self, item: str) -> str:
        return reverse(item)
