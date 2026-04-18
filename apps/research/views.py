from django.http import Http404
from django.views.generic import DetailView, ListView

from apps.site.models import SiteSettings

from .models import ResearchProject


class ResearchListView(ListView):
    template_name = "research/list.html"
    context_object_name = "research_projects"

    def dispatch(self, request, *args, **kwargs):
        if not SiteSettings.load().research_enabled:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ResearchProject.objects.filter(is_active=True)


class ResearchDetailView(DetailView):
    template_name = "research/detail.html"
    context_object_name = "research_project"

    def dispatch(self, request, *args, **kwargs):
        if not SiteSettings.load().research_enabled:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return ResearchProject.objects.filter(is_active=True)
