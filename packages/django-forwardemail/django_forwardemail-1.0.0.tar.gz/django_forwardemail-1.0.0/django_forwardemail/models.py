from django.contrib.sites.models import Site
from django.db import models


class EmailConfiguration(models.Model):
    """
    Email configuration for ForwardEmail API integration.

    This model stores the configuration needed to send emails through
    the ForwardEmail API service, with support for multiple sites.
    """

    api_key = models.CharField(
        max_length=255, help_text="ForwardEmail API key for authentication"
    )
    from_email = models.EmailField(help_text="Default email address to send from")
    from_name = models.CharField(
        max_length=255,
        help_text="The name that will appear in the From field of emails",
    )
    reply_to = models.EmailField(help_text="Default reply-to email address")
    site = models.ForeignKey(
        Site, on_delete=models.CASCADE, help_text="Site this configuration applies to"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.from_name} <{self.from_email}> ({self.site.domain})"

    class Meta:
        verbose_name = "Email Configuration"
        verbose_name_plural = "Email Configurations"
        unique_together = [["site"]]  # One configuration per site
