from django.db import models

from apps.site.about_defaults import public_lines, public_text

# ---------------------------------------------------------------------------
# Singleton mixin — ensures only one row exists in the DB for "global" models
# ---------------------------------------------------------------------------


class SingletonModel(models.Model):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, _ = cls.objects.get_or_create(pk=1)  # type: ignore[attr-defined]
        return obj


# ---------------------------------------------------------------------------
# SiteSettings  –  global site-wide metadata
# ---------------------------------------------------------------------------


class SiteSettings(SingletonModel):
    class PortfolioPreset(models.TextChoices):
        GENERIC = "generic", "Generic portfolio"
        SERVICE = "service", "Service / consultant portfolio"
        ACADEMIC = "academic", "Academic / research portfolio"

    site_name = models.CharField(
        max_length=120,
        default="",
        help_text="Your studio's display name. Shorter names (under 40 characters) work best in the homepage hero.",
    )
    portfolio_preset = models.CharField(
        max_length=20,
        choices=PortfolioPreset.choices,
        default=PortfolioPreset.GENERIC,
        help_text=(
            "Controls reusable homepage and navigation emphasis. "
            "Use Academic / research portfolio for researchers, PhD students, lecturers, scientists, consultants, and technical experts."
        ),
    )
    tagline = models.CharField(
        max_length=220,
        blank=True,
        default="Design shaped by purpose, context, and enduring quality.",
        help_text="One or two sentences describing your work. Under 140 characters fits most hero layouts cleanly.",
    )
    hero_label = models.CharField(
        max_length=60,
        blank=True,
        default="",
        help_text="Short descriptor shown above the studio name in the homepage hero (e.g. 'Design & Strategy'). Leave blank to omit.",
    )
    hero_compact = models.BooleanField(
        default=False,
        help_text="Compact hero text — use if your studio name or tagline is long and the hero looks crowded.",
    )
    nav_name = models.CharField(
        max_length=30,
        blank=True,
        default="",
        help_text=(
            "Overrides the automatic nav brand. Leave blank to let the system choose: "
            "short one- or two-word names (up to 18 characters) are shown in full; "
            "longer or multi-word names display as a derived monogram "
            "(e.g. \u2018BWK\u2019 for \u2018Beaumont Whitfield Kellerman Partnership\u2019). "
            "Set this field to an abbreviation like \u2018Strand Studio\u2019 or \u2018BWK Partners\u2019 "
            "if the automatic monogram is not what you want. A logo supersedes all text options."
        ),
    )
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    contact_email = models.EmailField(default="")
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    address = models.TextField(
        blank=True,
        help_text="Stored but not currently rendered on any public page. Reserved for future use or custom template additions.",
    )
    contact_response_time = models.CharField(
        max_length=60,
        blank=True,
        default="two working days",
        help_text=(
            "Response time shown to enquirers on the contact page and confirmation. "
            "E.g. 'two working days', '24 hours', 'one week'. "
            "Appears as: 'Enquiries reviewed within …'"
        ),
    )

    # Contact visibility controls
    show_email = models.BooleanField(
        default=True,
        help_text="Show the contact email address in the footer and contact sections.",
    )
    show_phone = models.BooleanField(
        default=False,
        help_text="Show the phone number in the footer and contact sections.",
    )
    show_location = models.BooleanField(
        default=True,
        help_text="Show the location in the footer identity and legal line.",
    )

    # Social links
    linkedin_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    behance_url = models.URLField(blank=True, help_text="Behance profile URL.")
    issuu_url = models.URLField(blank=True, help_text="Issuu profile or publication URL.")

    # Default social share image
    og_image = models.ImageField(
        upload_to="site/",
        blank=True,
        null=True,
        help_text="Default image used when sharing pages that have no cover image.",
    )

    # SEO — global default and per-page overrides
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Default meta description (homepage and fallback). Keep under 160 characters.",
    )
    about_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the About page. Keep under 160 characters.",
    )
    blog_meta_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional meta title for the Blog list page. Falls back to the page label.",
    )
    blog_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Blog list page. Falls back to the homepage meta description.",
    )
    projects_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Projects list page. Keep under 160 characters.",
    )
    services_meta_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional meta title for the Services page. Falls back to the page label.",
    )
    services_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Services page. Falls back to the homepage meta description.",
    )
    research_meta_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional meta title for the Research page. Falls back to the page label.",
    )
    research_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Research page. Falls back to the homepage meta description.",
    )
    publications_meta_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional meta title for the Publications page. Falls back to the page label.",
    )
    publications_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Publications page. Falls back to the homepage meta description.",
    )
    resume_meta_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Optional meta title for the Resume / CV page. Falls back to the page label.",
    )
    resume_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Resume / CV page. Falls back to the homepage meta description.",
    )
    contact_meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Meta description for the Contact page. Keep under 160 characters.",
    )
    google_analytics_id = models.CharField(
        max_length=30,
        blank=True,
        help_text="GA4 Measurement ID, e.g. G-XXXXXXXXXX.",
    )

    homepage_closing_text = models.CharField(
        max_length=220,
        blank=True,
        default="Ready to discuss a project? Bring a brief, a question, or an early idea.",
        help_text="Short closing invitation shown above the contact CTA on the homepage. Keep it under 120 characters.",
    )

    # Homepage featured projects — per-breakpoint visibility limits
    homepage_projects_mobile_count = models.PositiveSmallIntegerField(
        default=3,
        help_text="Max featured projects shown on mobile (up to 639px). Between 1 and 6.",
    )
    homepage_projects_tablet_count = models.PositiveSmallIntegerField(
        default=4,
        help_text="Max featured projects shown on tablet (640–959px). Between 1 and 6, at least mobile count.",
    )
    homepage_projects_desktop_count = models.PositiveSmallIntegerField(
        default=6,
        help_text="Max featured projects shown on desktop (960px+). Between 1 and 6, at least tablet count.",
    )

    # Optional modules
    blog_enabled = models.BooleanField(
        default=False,
        help_text="Show the optional Blog section in public navigation.",
    )
    services_enabled = models.BooleanField(
        default=False,
        help_text=(
            "Show the Services module in public navigation, footer, and homepage preview. "
            "Enable this for client sites that offer clearly defined services. "
            "Add Service items first so the page has content when you enable this."
        ),
    )
    testimonials_enabled = models.BooleanField(
        default=False,
        help_text=(
            "Show a testimonials section on the homepage. "
            "Testimonials are managed under Projects → Testimonials. "
            "Only active testimonials without a project association appear in the homepage section."
        ),
    )
    research_enabled = models.BooleanField(
        default=False,
        help_text=(
            "Show the Research module in public navigation, footer, and homepage preview. "
            "Add Research Projects first so the page has content when you enable this."
        ),
    )
    publications_enabled = models.BooleanField(
        default=False,
        help_text=(
            "Show the Publications module in public navigation, footer, and homepage preview. "
            "Add Publications first so the page has content when you enable this."
        ),
    )
    resume_enabled = models.BooleanField(
        default=False,
        help_text=(
            "Show the Resume / CV page in public navigation and footer. "
            "Add your headline, summary, and optionally a PDF download link via the Resume profile."
        ),
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"

    def clean(self):
        from django.core.exceptions import ValidationError

        errors = {}
        for field in (
            "homepage_projects_mobile_count",
            "homepage_projects_tablet_count",
            "homepage_projects_desktop_count",
        ):
            v = getattr(self, field)
            if not (1 <= v <= 6):
                errors[field] = "Must be between 1 and 6."
        if not errors:
            if self.homepage_projects_mobile_count > self.homepage_projects_tablet_count:
                errors["homepage_projects_mobile_count"] = "Mobile count cannot exceed tablet count."
            if self.homepage_projects_tablet_count > self.homepage_projects_desktop_count:
                errors["homepage_projects_tablet_count"] = "Tablet count cannot exceed desktop count."
        if errors:
            raise ValidationError(errors)


# ---------------------------------------------------------------------------
# AboutProfile  –  singleton about/bio page content
# ---------------------------------------------------------------------------


class AboutProfile(SingletonModel):
    class IdentityMode(models.TextChoices):
        PERSON = "person", "Person-led practice"
        STUDIO = "studio", "Studio-led practice"

    class PortraitMode(models.TextChoices):
        PORTRAIT = "portrait", "Show portrait"
        TEXT_ONLY = "text_only", "Text only"

    identity_mode = models.CharField(
        max_length=20,
        choices=IdentityMode.choices,
        default=IdentityMode.STUDIO,
        help_text="Choose whether the About page should introduce a named principal or the studio as a whole.",
    )
    principal_name = models.CharField(
        max_length=120,
        blank=True,
        help_text="Required for person-led practices. Leave blank for studio-led practices.",
    )
    principal_title = models.CharField(
        max_length=120,
        blank=True,
        help_text="Examples: Founder and Registered Architect, Principal Architect.",
    )
    professional_context = models.CharField(
        max_length=120,
        blank=True,
        help_text="A short truthful descriptor such as 'Solo practitioner' or 'Small studio'.",
    )
    one_line_bio = models.CharField(
        max_length=220,
        blank=True,
        help_text="Short public description shown in the hero.",
    )
    bio_summary = models.TextField(
        blank=True,
        help_text="Short factual summary of who you are, where you are based, and the kind of work you do.",
    )
    work_approach = models.TextField(
        blank=True,
        help_text="Explain how you work and how collaborators or consultants are involved.",
    )
    professional_standing = models.CharField(
        max_length=220,
        blank=True,
        help_text="Registration or professional standing shown publicly on the About page.",
    )
    education = models.TextField(
        blank=True,
        help_text="Education details — one per line.",
    )
    supporting_facts = models.TextField(
        blank=True,
        help_text="Concrete supporting facts — one per line. Use factual proof, not positioning language.",
    )
    approach = models.TextField(
        blank=True,
        help_text="Keep this practical and brief — ideally 2 to 3 sentences.",
    )
    experience_years = models.PositiveIntegerField(
        default=0,
        help_text="Years of professional experience. This value renders publicly — 0 is a placeholder; enter the real figure.",
    )
    closing_invitation = models.CharField(
        max_length=220,
        blank=True,
        help_text="Short closing invitation shown above the contact CTA.",
    )
    portrait_mode = models.CharField(
        max_length=20,
        choices=PortraitMode.choices,
        default=PortraitMode.TEXT_ONLY,
        help_text="Use text-only mode until a real portrait is ready. Public gray placeholders are intentionally disabled.",
    )
    portrait = models.ImageField(upload_to="about/", blank=True, null=True)
    cv_file = models.FileField(upload_to="about/cv/", blank=True, null=True)

    class Meta:
        verbose_name = "About Profile"
        verbose_name_plural = "About Profile"

    def __str__(self):
        return "About Profile"

    @staticmethod
    def _lines(value: str) -> list[str]:
        return [line.strip() for line in value.splitlines() if line.strip()]

    @property
    def education_lines(self) -> list[str]:
        return public_lines(self.education)

    @property
    def supporting_fact_lines(self) -> list[str]:
        return public_lines(self.supporting_facts)

    @property
    def has_concrete_supporting_fact(self) -> bool:
        return bool(self.education_lines or self.supporting_fact_lines)

    @property
    def public_professional_context(self) -> str:
        return public_text(self.professional_context)

    @property
    def public_work_approach(self) -> str:
        return public_text(self.work_approach)

    @property
    def public_professional_standing(self) -> str:
        return public_text(self.professional_standing)
