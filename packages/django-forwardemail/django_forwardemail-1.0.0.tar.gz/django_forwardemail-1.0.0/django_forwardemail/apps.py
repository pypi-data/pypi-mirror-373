from django.apps import AppConfig


class DjangoForwardEmailConfig(AppConfig):
    """Django app configuration for ForwardEmail integration."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_forwardemail"
    verbose_name = "Django ForwardEmail"

    def ready(self):
        """Initialize the app when Django starts."""
        # Import any signal handlers or other initialization code here
        pass
