from django.db import models
from django.utils.text import slugify


class Post(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=220, unique=True, blank=True)
    summary = models.CharField(
        max_length=300,
        blank=True,
        help_text="Short description shown in listings. Keep under 200 characters.",
    )
    body = models.TextField(blank=True)
    published_date = models.DateField(null=True, blank=True)
    is_published = models.BooleanField(default=False)
    tags = models.CharField(
        max_length=200,
        blank=True,
        help_text="Comma-separated tags, e.g. 'design, process, tools'.",
    )

    class Meta:
        verbose_name = "Post"
        verbose_name_plural = "Posts"
        ordering = ["-published_date", "title"]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def tag_list(self) -> list[str]:
        """Return a stripped list of individual tags."""
        return [t.strip() for t in self.tags.split(",") if t.strip()]
