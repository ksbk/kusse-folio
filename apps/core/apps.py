from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    # label is "core_runtime" rather than "core" because apps.site already
    # occupies the "core" label (preserved from when site models lived here).
    # See apps.site.apps.SiteConfigApp for the full explanation.
    label = "core_runtime"
    verbose_name = "Core Runtime"

    def ready(self):
        import apps.core.checks  # noqa: F401 - registers system checks
