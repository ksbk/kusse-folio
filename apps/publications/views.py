from django.http import Http404
from django.views.generic import ListView

from apps.site.models import SiteSettings

from .models import Publication


class PublicationListView(ListView):
    template_name = "publications/list.html"
    context_object_name = "publications"

    def dispatch(self, request, *args, **kwargs):
        if not SiteSettings.load().publications_enabled:
            raise Http404
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Publication.objects.filter(is_active=True)
