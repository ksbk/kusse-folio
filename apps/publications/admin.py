from django.contrib import admin

from .models import Publication


@admin.register(Publication)
class PublicationAdmin(admin.ModelAdmin):
    list_display = ("title", "authors", "venue", "year", "order", "is_featured", "is_active")
    list_editable = ("order", "is_featured", "is_active")
    list_filter = ("year", "is_featured", "is_active")
    search_fields = ("title", "authors", "venue", "abstract")
    fieldsets = (
        (
            "Publication",
            {
                "fields": ("title", "authors", "venue", "year", "abstract"),
                "description": (
                    "Core publication metadata. "
                    "Authors: list as they appear in the citation, e.g. 'Smith, J. &amp; Jones, A.'"
                ),
            },
        ),
        (
            "Links",
            {
                "fields": ("doi_url", "paper_url"),
                "description": "At least one link is recommended so readers can access the full text.",
            },
        ),
        (
            "Citation",
            {
                "fields": ("citation",),
                "description": "Optional full formatted citation. Shown below the abstract if provided.",
            },
        ),
        (
            "Display",
            {
                "fields": ("order", "is_featured", "is_active"),
            },
        ),
    )
