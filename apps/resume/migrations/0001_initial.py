from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="ResumeProfile",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("headline", models.CharField(blank=True, help_text="Short professional headline, e.g. 'Researcher & Educator in Human-Computer Interaction'.", max_length=200)),
                ("summary", models.TextField(blank=True, help_text="Professional summary shown at the top of the resume page.")),
                (
                    "cv_file",
                    models.FileField(
                        blank=True,
                        null=True,
                        upload_to="resume/",
                        help_text="Uploadable PDF or document. A download link will appear on the resume page when provided.",
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True, help_text="Automatically updated when the record is saved.")),
                ("is_active", models.BooleanField(default=True, help_text="Controls whether the resume page renders content or shows an empty state.")),
            ],
            options={
                "verbose_name": "Resume / CV Profile",
                "verbose_name_plural": "Resume / CV Profile",
            },
        ),
    ]
