from django.contrib import admin, messages

from ..models import AboutProfile, SiteSettings
from ..templatetags.core_tags import NAV_TEXT_MAX_CHARS, NAV_TEXT_MAX_WORDS, _compute_monogram

# ---------------------------------------------------------------------------
# SiteSettings
# ---------------------------------------------------------------------------


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Identity",
            {
                "fields": ("site_name", "tagline", "hero_label", "hero_compact", "nav_name", "logo", "og_image"),
                "description": (
                    "og_image is the default image used when sharing any page on social media. "
                    "hero_label appears above the studio name in the homepage hero; leave blank to omit it. "
                    "Enable hero_compact if the hero looks crowded with a long name or tagline. "
                    "nav_name is a shortened form of your practice name for the navigation bar — "
                    "leave blank to let the system choose: short one- or two-word names "
                    "(up to 18 characters) are shown in full; longer or multi-word names "
                    "automatically display as a derived monogram (e.g. 'BWK' for "
                    "'Beaumont Whitfield Kellerman Partnership'). "
                    "Set nav_name to override the automatic result with a specific abbreviation. "
                    "A logo supersedes all text options."
                ),
            },
        ),
        (
            "Contact",
            {
                "fields": ("contact_email", "phone", "location", "address"),
                "description": (
                    "contact_email is shown publicly on the site. "
                    "Contact-form notification delivery is configured separately "
                    "via the CONTACT_EMAIL environment variable."
                ),
            },
        ),
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
        (
            "SEO & Analytics",
            {
                "fields": (
                    "meta_description",
                    "about_meta_description",
                    "services_meta_description",
                    "projects_meta_description",
                    "contact_meta_description",
                    "google_analytics_id",
                )
            },
        ),
        (
            "Homepage — Featured Projects",
            {
                "fields": (
                    "homepage_projects_mobile_count",
                    "homepage_projects_tablet_count",
                    "homepage_projects_desktop_count",
                ),
                "description": (
                    "Controls how many featured projects are shown at each screen size. "
                    "Mobile \u2264 Tablet \u2264 Desktop. Each value must be between 1 and 6."
                ),
            },
        ),
    )

    def changeform_view(self, request, object_id=None, form_url="", extra_context=None):
        # Warn when site_name is blank. For GET requests we check the DB value;
        # for POST we check the submitted value so we don't fire after a successful fix.
        site_name_blank = (
            not request.POST.get("site_name")
            if request.method == "POST"
            else not SiteSettings.load().site_name
        )
        if site_name_blank:
            self.message_user(
                request,
                "Site name is blank. It appears in the page heading, navigation, and "
                "footer — set it before sharing or publishing the site.",
                level=messages.WARNING,
            )
        else:
            # Warn when a long site_name could crowd the navbar and no mitigation is set.
            if request.method == "POST":
                site_name_val = request.POST.get("site_name", "")
                nav_name_val  = request.POST.get("nav_name", "")
                logo_val      = request.POST.get("logo", "") or request.FILES.get("logo")
            else:
                s = SiteSettings.load()
                site_name_val = s.site_name
                nav_name_val  = s.nav_name
                logo_val      = s.logo
            if len(site_name_val) > 30 and not nav_name_val and not logo_val:
                self.message_user(
                    request,
                    "Your practice name is longer than 30 characters. Consider adding a short "
                    "Navigation Name, or uploading a logo, to ensure it fits on narrow screens.",
                    level=messages.INFO,
                )
            # Warn when the auto-computed monogram collapses to a single letter.
            # Warn when the auto-computed monogram collapses to a single letter.
            monogram_triggered = (
                len(site_name_val) > NAV_TEXT_MAX_CHARS
                or len(site_name_val.split()) > NAV_TEXT_MAX_WORDS
            )
            if monogram_triggered and not nav_name_val and not logo_val:
                monogram = _compute_monogram(site_name_val)
                if len(monogram) == 1:
                    self.message_user(
                        request,
                        f"The automatic nav monogram for this name would be a single letter "
                        f"(\u2018{monogram}\u2019). Consider setting a Nav Name to give visitors "
                        f"more context\u2014for example, an abbreviation like "
                        f"\u2018{monogram}CA\u2019 or a shortened version of the practice name.",
                        level=messages.WARNING,
                    )
        return super().changeform_view(request, object_id, form_url, extra_context)

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()


# ---------------------------------------------------------------------------
# AboutProfile
# ---------------------------------------------------------------------------


@admin.register(AboutProfile)
class AboutProfileAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            "Identity",
            {
                "fields": (
                    "identity_mode",
                    "principal_name",
                    "principal_title",
                    "practice_structure",
                    "one_line_practice_description",
                )
            },
        ),
        (
            "Content",
            {
                "fields": (
                    "practice_summary",
                    "project_leadership",
                    "approach",
                    "closing_invitation",
                ),
                "description": (
                    "Keep the About page factual. Practice summary explains what the practice "
                    "does; project leadership explains how work is led and where consultants fit in."
                ),
            },
        ),
        (
            "Professional Profile",
            {
                "fields": (
                    "professional_standing",
                    "education",
                    "supporting_facts",
                    "experience_years",
                ),
                "description": (
                    "Use concrete facts only. The public profile renders only when location, "
                    "professional standing, years in practice, and at least one supporting fact are present."
                ),
            },
        ),
        (
            "Files & Display",
            {
                "fields": ("portrait_mode", "portrait", "cv_file"),
                "description": (
                    "Text-only mode is allowed, but the public page will not show a gray portrait placeholder."
                ),
            },
        ),
    )

    def has_add_permission(self, request):
        return not AboutProfile.objects.exists()
