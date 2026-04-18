from django.contrib import admin

from .models import ResumeProfile


@admin.register(ResumeProfile)
class ResumeProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Profile",
            {
                "fields": ("headline", "summary", "is_active"),
                "description": (
                    "The headline and summary appear at the top of the public resume page. "
                    "This is a singleton record — there is only one resume profile."
                ),
            },
        ),
        (
            "Document",
            {
                "fields": ("cv_file", "updated_at"),
                "description": "Upload a PDF to enable the download button on the resume page.",
            },
        ),
    )
    readonly_fields = ("updated_at",)

    def has_add_permission(self, request):
        # Enforce singleton via admin: disallow creating a second row.
        return not ResumeProfile.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False
