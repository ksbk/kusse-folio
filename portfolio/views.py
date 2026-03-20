import logging

from django.conf import settings as django_settings
from django.core.mail import EmailMessage
from django.shortcuts import redirect, render
from django.views.generic import DetailView, ListView, TemplateView

from .forms import PROJECT_TYPE_CHOICES, ContactForm
from .models import AboutProfile, Project, Service, SiteSettings, Testimonial

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Home
# ---------------------------------------------------------------------------


class HomeView(TemplateView):
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["featured_projects"] = Project.objects.filter(featured=True).order_by("order")[:6]
        # Exclude featured projects to avoid showing the same work twice on the homepage.
        ctx["all_projects"] = Project.objects.filter(featured=False).order_by("order")[:9]
        ctx["services"] = Service.objects.filter(active=True)
        ctx["testimonials"] = Testimonial.objects.filter(active=True)
        ctx["about"] = AboutProfile.load()
        site = SiteSettings.load()
        if site.og_image:
            ctx["og_image"] = site.og_image.url
        return ctx


# ---------------------------------------------------------------------------
# Projects
# ---------------------------------------------------------------------------


class ProjectListView(ListView):
    model = Project
    template_name = "projects/list.html"
    context_object_name = "projects"
    paginate_by = 12

    def get_queryset(self):
        qs = Project.objects.all().order_by("order", "-year")
        category = self.request.GET.get("category")
        if category:
            qs = qs.filter(category=category)
        return qs

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["categories"] = Project.CATEGORY_CHOICES
        ctx["active_category"] = self.request.GET.get("category", "")
        return ctx


class ProjectDetailView(DetailView):
    model = Project
    template_name = "projects/detail.html"
    context_object_name = "project"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        project = self.get_object()
        ctx["gallery"] = project.images.filter(image_type="gallery")
        ctx["drawings"] = project.images.exclude(image_type="gallery")
        ctx["related"] = (
            Project.objects.filter(category=project.category)
            .exclude(pk=project.pk)
            .order_by("order")[:3]
        )
        ctx["testimonials"] = project.testimonials.filter(active=True)
        if project.cover_image:
            ctx["og_image"] = project.cover_image.url
        else:
            site = SiteSettings.load()
            if site.og_image:
                ctx["og_image"] = site.og_image.url
        return ctx


# ---------------------------------------------------------------------------
# About
# ---------------------------------------------------------------------------


class AboutView(TemplateView):
    template_name = "about.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["profile"] = AboutProfile.load()
        site = SiteSettings.load()
        if site.og_image:
            ctx["og_image"] = site.og_image.url
        return ctx


# ---------------------------------------------------------------------------
# Services
# ---------------------------------------------------------------------------


class ServicesView(ListView):
    model = Service
    template_name = "services.html"
    context_object_name = "services"
    queryset = Service.objects.filter(active=True)


# ---------------------------------------------------------------------------
# Contact
# ---------------------------------------------------------------------------


def contact_view(request):
    if request.method == "POST":
        form = ContactForm(request.POST)
        if form.is_valid():
            inquiry = form.save()
            # Notify site owner — failure is non-fatal (form already saved to DB).
            # Reply-To is set so the architect can reply directly from their email client.
            try:
                msg = EmailMessage(
                    subject=f"New enquiry from {inquiry.name}",
                    body=(
                        f"Name: {inquiry.name}\n"
                        f"Email: {inquiry.email}\n"
                        f"Company: {inquiry.company}\n"
                        f"Project type: {inquiry.project_type}\n"
                        f"Location: {inquiry.location}\n"
                        f"Budget: {inquiry.budget_range}\n"
                        f"Timeline: {inquiry.timeline}\n\n"
                        f"Message:\n{inquiry.message}"
                    ),
                    from_email=django_settings.DEFAULT_FROM_EMAIL,
                    to=[django_settings.CONTACT_EMAIL],
                    reply_to=[inquiry.email],
                )
                msg.send()
            except Exception:
                logger.exception("Contact email failed for inquiry pk=%s", inquiry.pk)
            return redirect("contact_success")
    else:
        initial: dict[str, str] = {}
        project_type = request.GET.get("project_type", "").strip()
        if project_type:
            valid_types = {c[0] for c in PROJECT_TYPE_CHOICES if c[0]}
            if project_type in valid_types:
                initial["project_type"] = project_type
        form = ContactForm(initial=initial)
    return render(request, "contact.html", {"form": form})


def contact_success_view(request):
    return render(request, "contact_success.html")
