from django.views.generic import TemplateView

from apps.core.models import AboutProfile
from apps.projects.models import Project, Testimonial
from apps.services.models import Service


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        featured_projects = list(
            Project.objects.with_preview_media().filter(featured=True).order_by("order")[:4]
        )
        remaining_slots = max(0, 4 - len(featured_projects))
        supporting_projects = list(
            Project.objects.with_preview_media()
            .filter(featured=False)
            .order_by("order")[:remaining_slots]
        )
        homepage_projects = featured_projects + supporting_projects
        ctx["homepage_projects"] = homepage_projects
        ctx["hero_project"] = homepage_projects[0] if homepage_projects else None
        ctx["services"] = Service.objects.filter(active=True)
        ctx["testimonials"] = Testimonial.objects.filter(active=True)
        ctx["about"] = AboutProfile.load()
        return ctx


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = AboutProfile.load()
        return ctx


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"
