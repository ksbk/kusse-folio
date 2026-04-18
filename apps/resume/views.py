from django.http import Http404
from django.views.generic import TemplateView

from apps.site.models import SiteSettings

from .models import ResumeProfile


class ResumeView(TemplateView):
    template_name = "resume/page.html"

    def dispatch(self, request, *args, **kwargs):
        if not SiteSettings.load().resume_enabled:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["resume"] = ResumeProfile.load()
        return ctx
