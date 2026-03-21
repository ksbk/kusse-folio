from django.contrib.sitemaps import Sitemap

from .models import Project


class ProjectSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.8

    def items(self):
        return Project.objects.all().order_by("order", "-year")

    def lastmod(self, obj: Project):
        return obj.updated_at

    def location(self, obj: Project) -> str:
        return obj.get_absolute_url()
