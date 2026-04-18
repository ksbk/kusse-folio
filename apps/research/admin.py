from django.contrib import admin

from .models import ResearchProject


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ("title", "status", "order", "is_featured", "is_active")
    list_editable = ("order", "is_featured", "is_active")
    list_filter = ("status", "is_featured", "is_active")
    prepopulated_fields = {"slug": ("title",)}
    search_fields = ("title", "summary")
    fieldsets = (
        (
            "Content",
            {
                "fields": ("title", "slug", "summary", "description"),
            },
        ),
        (
            "Status & Ordering",
            {
                "fields": ("status", "order", "is_featured", "is_active"),
            },
        ),
    )
