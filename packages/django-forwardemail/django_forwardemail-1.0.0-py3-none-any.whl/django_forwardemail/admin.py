from django.contrib import admin
from django.contrib.sites.models import Site

from .models import EmailConfiguration


@admin.register(EmailConfiguration)
class EmailConfigurationAdmin(admin.ModelAdmin):
    """
    Django admin configuration for EmailConfiguration model.

    Provides a user-friendly interface for managing ForwardEmail
    configurations across multiple sites.
    """

    list_display = (
        "site",
        "from_name",
        "from_email",
        "reply_to",
        "updated_at",
    )
    list_select_related = ("site",)
    search_fields = ("site__domain", "from_name", "from_email", "reply_to")
    readonly_fields = ("created_at", "updated_at")
    list_filter = ("site", "updated_at", "created_at")

    fieldsets = (
        (None, {"fields": ("site",)}),
        (
            "Email Settings",
            {
                "fields": ("api_key", ("from_name", "from_email"), "reply_to"),
                "description": (
                    "Configure the email settings. The From field in emails "
                    'will appear as "From Name <from@email.com>"'
                ),
            },
        ),
        (
            "Timestamps",
            {"fields": ("created_at", "updated_at"), "classes": ("collapse",)},
        ),
    )

    def get_queryset(self, request):
        """Optimize queryset with select_related."""
        return super().get_queryset(request).select_related("site")

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Customize the site field to show ordered domains."""
        if db_field.name == "site":
            kwargs["queryset"] = Site.objects.all().order_by("domain")
        return super().formfield_for_foreignkey(db_field, request, **kwargs)
