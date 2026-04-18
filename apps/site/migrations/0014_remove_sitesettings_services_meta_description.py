from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0013_rename_aboutprofile_fields"),
    ]

    operations = [
        migrations.RemoveField(
            model_name="sitesettings",
            name="services_meta_description",
        ),
    ]
