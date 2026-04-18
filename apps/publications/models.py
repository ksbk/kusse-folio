from django.db import models


class Publication(models.Model):
    title = models.CharField(
        max_length=300,
        help_text="Full publication title.",
    )
    authors = models.CharField(
        max_length=400,
        blank=True,
        help_text="Author(s) as they should appear in the listing, e.g. 'Smith, J., Jones, A.'",
    )
    venue = models.CharField(
        max_length=300,
        blank=True,
        help_text="Journal, conference, or book title.",
    )
    year = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        help_text="Publication year.",
    )
    abstract = models.TextField(
        blank=True,
        help_text="Abstract or short description shown in the listing.",
    )
    doi_url = models.URLField(
        blank=True,
        help_text="DOI link, e.g. https://doi.org/10.xxxx/xxxxxx",
    )
    paper_url = models.URLField(
        blank=True,
        help_text="Direct link to the paper PDF or publisher page.",
    )
    citation = models.TextField(
        blank=True,
        help_text="Full formatted citation, shown below the abstract if present.",
    )
    order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )
    is_featured = models.BooleanField(
        default=False,
        help_text="Featured publications appear in the homepage preview.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Only active publications appear on the public publications page.",
    )

    class Meta:
        ordering = ["-year", "order", "title"]
        verbose_name = "Publication"
        verbose_name_plural = "Publications"

    def __str__(self) -> str:
        year_part = f" ({self.year})" if self.year else ""
        return f"{self.title}{year_part}"
