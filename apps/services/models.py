from django.db import models
from django.utils.text import slugify

from apps.core.enquiry_types import SERVICE_SLUG_TO_ENQUIRY_TYPE


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

    @property
    def contact_project_type(self) -> str:
        return SERVICE_SLUG_TO_ENQUIRY_TYPE.get(self.slug, "Other")

    def deliverables_list(self):
        return [d.strip() for d in self.deliverables.splitlines() if d.strip()]
