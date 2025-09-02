from django.apps import AppConfig


class DjangoSupportalConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "django_supportal"
    verbose_name = "django supportal"

    def ready(self):
        # import signals here if needed
        pass
