from django.db import models
from django.utils.text import slugify

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
    site_name = models.CharField(max_length=120, default="Jeannot Tsirenge")
    tagline = models.CharField(
        max_length=220,
        default="Architectural design shaped by context, clarity, and identity.",
    )
    logo = models.ImageField(upload_to="site/", blank=True, null=True)
    contact_email = models.EmailField(default="contact@jeannot-tsirenge.com")
    phone = models.CharField(max_length=40, blank=True)
    location = models.CharField(max_length=120, blank=True)
    address = models.TextField(blank=True)

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

    # SEO
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Shown in search results. Keep under 160 characters.",
    )
    google_analytics_id = models.CharField(
        max_length=30,
        blank=True,
        help_text="GA4 Measurement ID, e.g. G-XXXXXXXXXX.",
    )

    class Meta:
        verbose_name = "Site Settings"
        verbose_name_plural = "Site Settings"

    def __str__(self):
        return "Site Settings"


# ---------------------------------------------------------------------------
# AboutProfile  –  singleton about/bio page content
# ---------------------------------------------------------------------------


class AboutProfile(SingletonModel):
    headline = models.CharField(max_length=200, blank=True)
    intro = models.TextField(
        blank=True,
        help_text="Short intro paragraph shown at the top of the About page.",
    )
    biography = models.TextField(blank=True)
    philosophy = models.TextField(blank=True)
    credentials = models.TextField(
        blank=True,
        help_text="Education, certifications, memberships — one per line.",
    )
    experience_years = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=120, blank=True)
    portrait = models.ImageField(upload_to="about/", blank=True, null=True)
    cv_file = models.FileField(upload_to="about/cv/", blank=True, null=True)

    class Meta:
        verbose_name = "About Profile"
        verbose_name_plural = "About Profile"

    def __str__(self):
        return "About Profile"


# ---------------------------------------------------------------------------
# Service
# ---------------------------------------------------------------------------


class Service(models.Model):
    title = models.CharField(max_length=120)
    slug = models.SlugField(unique=True, blank=True)
    summary = models.CharField(max_length=250)
    description = models.TextField(blank=True)
    who_for = models.CharField(max_length=250, blank=True)
    value_proposition = models.TextField(blank=True)
    deliverables = models.TextField(
        blank=True,
        help_text="One deliverable per line.",
    )
    icon_name = models.CharField(
        max_length=60,
        blank=True,
        help_text="Optional icon identifier (e.g. 'pen-ruler', 'building').",
    )
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Service"
        verbose_name_plural = "Services"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def deliverables_list(self):
        return [d.strip() for d in self.deliverables.splitlines() if d.strip()]


# ---------------------------------------------------------------------------
# Project
# ---------------------------------------------------------------------------


class Project(models.Model):
    CATEGORY_CHOICES = [
        ("residential", "Residential"),
        ("commercial", "Commercial"),
        ("cultural", "Cultural"),
        ("mixed_use", "Mixed Use"),
        ("interior", "Interior Architecture"),
        ("concept", "Conceptual"),
        ("renovation", "Renovation & Adaptive Reuse"),
        ("competition", "Competition"),
        ("other", "Other"),
    ]
    STATUS_CHOICES = [
        ("completed", "Completed"),
        ("in_progress", "In Progress"),
        ("concept", "Concept"),
        ("competition", "Competition Entry"),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, blank=True)
    short_description = models.CharField(
        max_length=300,
        help_text="One or two clear sentences shown on project cards and in search results. Under 160 characters is ideal.",
    )
    category = models.CharField(max_length=40, choices=CATEGORY_CHOICES, default="other")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="completed")

    # Location & metadata
    location = models.CharField(max_length=150, blank=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    client = models.CharField(max_length=150, blank=True)
    area = models.CharField(max_length=60, blank=True, help_text='e.g. "2 400 m²"')
    services_provided = models.TextField(
        blank=True,
        help_text="Scope of services delivered, e.g. 'Concept design through construction administration.' One service per line.",
    )

    # Story
    overview = models.TextField(blank=True, help_text="Project introduction paragraph.")
    challenge = models.TextField(blank=True)
    concept = models.TextField(blank=True)
    process = models.TextField(
        blank=True,
        help_text="Optional — describe the design and construction process, methods used, or team collaboration.",
    )
    outcome = models.TextField(blank=True)

    # Media
    cover_image = models.ImageField(
        upload_to="projects/covers/",
        blank=True,
        null=True,
        help_text="Recommended: at least 1600 × 900 px, JPEG or WebP. Used as the hero image and OpenGraph share image.",
    )

    # Flags
    featured = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)

    # SEO
    seo_title = models.CharField(
        max_length=70,
        blank=True,
        help_text="Overrides project title in browser tab and search results. Ideal length: under 60 characters.",
    )
    seo_description = models.CharField(
        max_length=160,
        blank=True,
        help_text="Overrides short description in search results. Under 160 characters.",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "-year", "title"]
        verbose_name = "Project"
        verbose_name_plural = "Projects"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse

        return reverse("project_detail", kwargs={"slug": self.slug})

    def get_seo_title(self):
        return self.seo_title or self.title

    def get_seo_description(self):
        return self.seo_description or self.short_description


# ---------------------------------------------------------------------------
# ProjectImage
# ---------------------------------------------------------------------------


class ProjectImage(models.Model):
    TYPE_CHOICES = [
        ("gallery", "Gallery"),
        ("plan", "Floor Plan"),
        ("section", "Section / Elevation"),
        ("sketch", "Sketch"),
        ("detail", "Detail"),
        ("render", "Render"),
    ]

    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="projects/gallery/")
    caption = models.CharField(max_length=200, blank=True)
    alt_text = models.CharField(
        max_length=200,
        blank=True,
        help_text="Descriptive alt text for screen readers. Falls back to caption if empty.",
    )
    order = models.PositiveIntegerField(default=0)
    image_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default="gallery")

    class Meta:
        ordering = ["order"]
        verbose_name = "Project Image"
        verbose_name_plural = "Project Images"

    def __str__(self):
        return f"{self.project.title} — image {self.order}"

    def get_alt_text(self):
        """Return alt_text if set, falling back to caption, then project title."""
        return self.alt_text or self.caption or self.project.title


# ---------------------------------------------------------------------------
# Testimonial
# ---------------------------------------------------------------------------


class Testimonial(models.Model):
    name = models.CharField(max_length=120)
    role = models.CharField(max_length=120, blank=True)
    company = models.CharField(max_length=120, blank=True)
    quote = models.TextField()
    project = models.ForeignKey(
        Project,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="testimonials",
    )
    order = models.PositiveIntegerField(default=0)
    active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]
        verbose_name = "Testimonial"
        verbose_name_plural = "Testimonials"

    def __str__(self):
        return f"{self.name} — {self.company}"


# ---------------------------------------------------------------------------
# ContactInquiry
# ---------------------------------------------------------------------------


class ContactInquiry(models.Model):
    STATUS_CHOICES = [
        ("new", "New"),
        ("read", "Read"),
        ("replied", "Replied"),
        ("archived", "Archived"),
    ]

    name = models.CharField(max_length=150)
    email = models.EmailField()
    company = models.CharField(max_length=150, blank=True)
    project_type = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)
    budget_range = models.CharField(max_length=100, blank=True)
    timeline = models.CharField(max_length=100, blank=True)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="new")
    notes = models.TextField(
        blank=True,
        help_text="Internal notes for admin workflow — not visible to the client.",
    )

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Contact Inquiry"
        verbose_name_plural = "Contact Inquiries"

    def __str__(self):
        return f"{self.name} <{self.email}> — {self.created_at:%Y-%m-%d}"
