from django.apps import AppConfig


class SiteConfigApp(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.site"
    # label is preserved as "core" because all migrations for this app were
    # created under that label.  Renaming it would require a migration squash
    # and coordinated changes to every existing migration file.  The runtime
    # behaviour is correct; this is a historical alias, not a bug.
    # See also: apps.core.apps.CoreConfig, which uses label="core_runtime" to
    # avoid collision with this label.
    label = "core"
    verbose_name = "Site Configuration"
