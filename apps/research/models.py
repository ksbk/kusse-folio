from django.db import models
from django.utils.text import slugify


class ResearchProject(models.Model):
    class Status(models.TextChoices):
        ONGOING = "ongoing", "Ongoing"
        COMPLETED = "completed", "Completed"
        FORTHCOMING = "forthcoming", "Forthcoming"

    title = models.CharField(
        max_length=200,
        help_text="Research project title as it appears in listings.",
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
    )
    summary = models.CharField(
        max_length=400,
        blank=True,
        help_text="One or two sentence overview shown in the research list. Under 280 characters.",
    )
    description = models.TextField(
        blank=True,
        help_text="Full description shown on the detail page.",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        blank=True,
        default="",
        help_text="Current research status. Leave blank to omit from display.",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured research projects appear in the homepage preview.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active projects appear on the public research page.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["order", "title"]
        verbose_name = "Research Project"
        verbose_name_plural = "Research Projects"

    def __str__(self) -> str:
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self) -> str:
        from django.urls import reverse
        return reverse("research:detail", kwargs={"slug": self.slug})
