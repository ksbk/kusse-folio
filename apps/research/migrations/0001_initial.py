import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ResearchProject",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Research project title as it appears in listings.", max_length=200)),
                ("slug", models.SlugField(blank=True, max_length=220, unique=True)),
                ("summary", models.CharField(blank=True, help_text="One or two sentence overview shown in the research list. Under 280 characters.", max_length=400)),
                ("description", models.TextField(blank=True, help_text="Full description shown on the detail page.")),
                ("status", models.CharField(blank=True, choices=[("ongoing", "Ongoing"), ("completed", "Completed"), ("forthcoming", "Forthcoming")], default="", help_text="Current research status. Leave blank to omit from display.", max_length=20)),
                ("order", models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")),
                ("is_featured", models.BooleanField(default=False, help_text="Featured research projects appear in the homepage preview.")),
                ("is_active", models.BooleanField(default=True, help_text="Only active projects appear on the public research page.")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Research Project",
                "verbose_name_plural": "Research Projects",
                "ordering": ["order", "title"],
            },
        ),
    ]
