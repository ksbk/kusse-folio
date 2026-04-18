from django.db import models


class ResumeProfile(models.Model):
    """
    A singleton-style model for the public resume/CV page.
    Stores a headline, summary, and an optional downloadable file.
    Structured experience sections (jobs, education, skills) are not yet included
    and can be added in a future version.
    """

    headline = models.CharField(
        max_length=200,
        blank=True,
        help_text="Short professional headline, e.g. 'Researcher & Educator in Human-Computer Interaction'.",
    )
    summary = models.TextField(
        blank=True,
        help_text="Professional summary shown at the top of the resume page.",
    )
    cv_file = models.FileField(
        upload_to="resume/",
        blank=True,
        null=True,
        help_text="Uploadable PDF or document. A download link will appear on the resume page when provided.",
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Automatically updated when the record is saved.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Controls whether the resume page renders content or shows an empty state.",
    )

    class Meta:
        verbose_name = "Resume / CV Profile"
        verbose_name_plural = "Resume / CV Profile"

    def __str__(self) -> str:
        return self.headline or "Resume Profile"

    def save(self, *args, **kwargs):
        # Enforce singleton: only one row, always pk=1.
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def load(cls) -> "ResumeProfile":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj
