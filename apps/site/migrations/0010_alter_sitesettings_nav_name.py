from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0009_sitesettings_contact_response_time"),
    ]

    operations = [
        migrations.AlterField(
            model_name="sitesettings",
            name="nav_name",
            field=models.CharField(
                blank=True,
                default="",
                help_text=(
                    "Overrides the automatic nav brand. Leave blank to let the system choose: "
                    "short one- or two-word names (up to 18 characters) are shown in full; "
                    "longer or multi-word names display as a derived monogram "
                    "(e.g. \u2018BWK\u2019 for \u2018Beaumont Whitfield Kellerman Partnership\u2019). "
                    "Set this field to an abbreviation like \u2018Strand Architecture\u2019 or \u2018BWK Partnership\u2019 "
                    "if the automatic monogram is not what you want. "
                    "A logo supersedes all text options."
                ),
                max_length=30,
            ),
        ),
    ]
