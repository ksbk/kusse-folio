from django.views.generic import TemplateView

from apps.projects.models import Project, Testimonial
from apps.site.models import AboutProfile, SiteSettings


class HomeView(TemplateView):
    template_name = "pages/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        site = SiteSettings.load()
        desktop_max = site.homepage_projects_desktop_count
        featured = list(
            Project.objects.with_preview_media()
            .filter(featured=True)
            .order_by("order")[:desktop_max]
        )
        if featured:
            homepage_projects = featured
        else:
            homepage_projects = list(
                Project.objects.with_preview_media()
                .order_by("order")[:desktop_max]
            )
        ctx["homepage_projects"] = homepage_projects
        ctx["homepage_projects_count"] = len(homepage_projects)
        ctx["hp_mobile"] = site.homepage_projects_mobile_count
        ctx["hp_tablet"] = site.homepage_projects_tablet_count
        ctx["hp_desktop"] = site.homepage_projects_desktop_count
        ctx["hero_project"] = homepage_projects[0] if homepage_projects else None
        ctx["homepage_closing_text"] = (
            site.homepage_closing_text
            or "Ready to discuss a project? Bring a brief, a question, or an early idea."
        )

        if site.services_enabled:
            from apps.services.models import ServiceItem
            ctx["homepage_services"] = list(ServiceItem.objects.filter(active=True)[:6])
        else:
            ctx["homepage_services"] = []

        if site.testimonials_enabled:
            ctx["homepage_testimonials"] = list(
                Testimonial.objects.filter(active=True, project__isnull=True).order_by("order")[:6]
            )
        else:
            ctx["homepage_testimonials"] = []

        if site.research_enabled:
            from apps.research.models import ResearchProject
            ctx["homepage_research"] = list(
                ResearchProject.objects.filter(is_active=True, is_featured=True).order_by("order")[:4]
            )
        else:
            ctx["homepage_research"] = []

        if site.publications_enabled:
            from apps.publications.models import Publication
            ctx["homepage_publications"] = list(
                Publication.objects.filter(is_active=True, is_featured=True).order_by("-year", "order")[:4]
            )
        else:
            ctx["homepage_publications"] = []

        return ctx


class AboutView(TemplateView):
    template_name = "pages/about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        profile = AboutProfile.load()
        site = SiteSettings.load()

        show_portrait = (
            profile.portrait_mode == AboutProfile.PortraitMode.PORTRAIT and bool(profile.portrait)
        )
        hero_title = site.site_name or "About"
        hero_meta = ""

        if (
            profile.identity_mode == AboutProfile.IdentityMode.PERSON
            and profile.principal_name
        ):
            hero_title = profile.principal_name
            hero_meta = ", ".join(
                part for part in [profile.principal_title, site.site_name] if part
            )
        elif profile.public_professional_context:
            hero_meta = profile.public_professional_context

        show_professional_profile = bool(
            site.location
            and profile.public_professional_standing
            and profile.experience_years
            and profile.has_concrete_supporting_fact
        )

        ctx["profile"] = profile
        ctx["about_hero_title"] = hero_title
        ctx["about_hero_meta"] = hero_meta
        ctx["show_about_portrait"] = show_portrait
        ctx["show_professional_profile"] = show_professional_profile
        ctx["about_public_location"] = site.location
        return ctx


class PrivacyView(TemplateView):
    template_name = "pages/privacy.html"


class WebsiteServiceView(TemplateView):
    template_name = "pages/website_service.html"
