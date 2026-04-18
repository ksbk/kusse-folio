from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0018_alter_clientprofile_website_domain_helptext"),
    ]

    operations = [
        migrations.AddField(
            model_name="sitesettings",
            name="research_enabled",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Show the Research module in public navigation, footer, and homepage preview. "
                    "Add Research Projects first so the page has content when you enable this."
                ),
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="publications_enabled",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Show the Publications module in public navigation, footer, and homepage preview. "
                    "Add Publications first so the page has content when you enable this."
                ),
            ),
        ),
        migrations.AddField(
            model_name="sitesettings",
            name="resume_enabled",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Show the Resume / CV page in public navigation and footer. "
                    "Add your headline, summary, and optionally a PDF download link via the Resume profile."
                ),
            ),
        ),
    ]
