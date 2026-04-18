from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Publication",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("title", models.CharField(help_text="Full publication title.", max_length=300)),
                ("authors", models.CharField(blank=True, help_text="Author(s) as they should appear in the listing, e.g. 'Smith, J., Jones, A.'", max_length=400)),
                ("venue", models.CharField(blank=True, help_text="Journal, conference, or book title.", max_length=300)),
                ("year", models.PositiveSmallIntegerField(blank=True, help_text="Publication year.", null=True)),
                ("abstract", models.TextField(blank=True, help_text="Abstract or short description shown in the listing.")),
                ("doi_url", models.URLField(blank=True, help_text="DOI link, e.g. https://doi.org/10.xxxx/xxxxxx")),
                ("paper_url", models.URLField(blank=True, help_text="Direct link to the paper PDF or publisher page.")),
                ("citation", models.TextField(blank=True, help_text="Full formatted citation, shown below the abstract if present.")),
                ("order", models.PositiveIntegerField(default=0, help_text="Lower numbers appear first.")),
                ("is_featured", models.BooleanField(default=False, help_text="Featured publications appear in the homepage preview.")),
                ("is_active", models.BooleanField(default=True, help_text="Only active publications appear on the public publications page.")),
            ],
            options={
                "verbose_name": "Publication",
                "verbose_name_plural": "Publications",
                "ordering": ["-year", "order", "title"],
            },
        ),
    ]
