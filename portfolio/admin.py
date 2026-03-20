from django.contrib import admin
from django.utils.html import format_html

from .models import (
    AboutProfile,
    ContactInquiry,
    Project,
    ProjectImage,
    Service,
    SiteSettings,
    Testimonial,
)

# ---------------------------------------------------------------------------
# SiteSettings
# ---------------------------------------------------------------------------


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Identity", {"fields": ("site_name", "tagline", "logo")}),
        ("Contact", {"fields": ("contact_email", "phone", "location", "address")}),
        (
            "Social",
            {
                "fields": (
                    "linkedin_url",
                    "instagram_url",
                    "facebook_url",
                    "behance_url",
                    "issuu_url",
                )
            },
        ),
        ("SEO & Analytics", {"fields": ("meta_description", "og_image", "google_analytics_id")}),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


# ---------------------------------------------------------------------------
# AboutProfile
# ---------------------------------------------------------------------------


@admin.register(AboutProfile)
class AboutProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Header", {"fields": ("headline", "intro")}),
        ("Content", {"fields": ("biography", "philosophy", "credentials")}),
        ("Details", {"fields": ("experience_years", "location")}),
        ("Files", {"fields": ("portrait", "cv_file")}),
    )

    def has_add_permission(self, request):
        return not AboutProfile.objects.exists()


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "summary", "order", "active")
    list_editable = ("order", "active")
    prepopulated_fields = {"slug": ("title",)}
    fieldsets = (
        (None, {"fields": ("title", "slug", "summary", "order", "active", "icon_name")}),
        ("Detail", {"fields": ("description", "who_for", "value_proposition", "deliverables")}),
    )


# ---------------------------------------------------------------------------
# Project + inline images
# ---------------------------------------------------------------------------


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ("image", "image_type", "caption", "alt_text", "order")
    ordering = ("order",)


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = (
        "cover_thumb",
        "title",
        "category",
        "status",
        "year",
        "location",
        "featured",
        "order",
    )
    list_display_links = ("cover_thumb", "title")
    list_editable = ("featured", "order", "year", "status")
    list_filter = ("category", "status", "featured")
    search_fields = ("title", "location", "client")
    prepopulated_fields = {"slug": ("title",)}
    inlines = [ProjectImageInline]
    fieldsets = (
        ("Identity", {"fields": ("title", "slug", "short_description", "cover_image")}),
        ("Classification", {"fields": ("category", "status", "featured", "order")}),
        ("Metadata", {"fields": ("location", "year", "client", "area", "services_provided")}),
        ("Story", {"fields": ("overview", "challenge", "concept", "process", "outcome")}),
        ("SEO", {"fields": ("seo_title", "seo_description"), "classes": ("collapse",)}),
    )

    @admin.display(description="Cover")
    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height:48px;width:72px;object-fit:cover;border-radius:3px;">',
                obj.cover_image.url,
            )
        return "—"


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display = ("name", "role", "company", "project", "order", "active")
    list_editable = ("order", "active")
    list_filter = ("active",)
    search_fields = ("name", "quote", "company")


# ---------------------------------------------------------------------------
# ContactInquiry
# ---------------------------------------------------------------------------


@admin.register(ContactInquiry)
class ContactInquiryAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "company", "project_type", "created_at", "status")
    list_filter = ("status",)
    date_hierarchy = "created_at"
    search_fields = ("name", "email", "company", "message")
    readonly_fields = (
        "name",
        "email",
        "company",
        "project_type",
        "location",
        "budget_range",
        "timeline",
        "message",
        "created_at",
    )
    list_editable = ("status",)
    fieldsets = (
        (
            "Inquiry",
            {
                "fields": (
                    "name",
                    "email",
                    "company",
                    "project_type",
                    "location",
                    "budget_range",
                    "timeline",
                    "message",
                    "created_at",
                )
            },
        ),
        ("Admin", {"fields": ("status", "notes")}),
    )

    def has_add_permission(self, request):
        return False
