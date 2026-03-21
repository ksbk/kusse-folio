from django.views.generic import TemplateView

from apps.core.models import AboutProfile
from apps.projects.models import Project, Testimonial
from apps.services.models import Service


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured_projects"] = Project.objects.filter(featured=True).order_by("order")[:6]
        # Exclude featured projects to avoid showing the same work twice on the homepage.
        ctx["all_projects"] = Project.objects.filter(featured=False).order_by("order")[:9]
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
