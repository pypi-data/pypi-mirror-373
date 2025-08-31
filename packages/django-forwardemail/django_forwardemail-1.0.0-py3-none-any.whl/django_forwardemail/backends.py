from collections.abc import Sequence
from typing import TYPE_CHECKING

from django.core.mail.backends.base import BaseEmailBackend
from django.core.mail.message import (
    EmailMessage,
    EmailMultiAlternatives,
    sanitize_address,
)

from .services import ForwardEmailService

if TYPE_CHECKING:
    from django.contrib.sites.models import Site


class ForwardEmailBackend(BaseEmailBackend):
    """
    Django email backend for ForwardEmail API.

    This backend integrates with Django's email system to send emails
    through the ForwardEmail API service.
    """

    def __init__(self, fail_silently: bool = False, **kwargs):
        """
        Initialize the ForwardEmail backend.

        Args:
            fail_silently: Whether to suppress exceptions
            **kwargs: Additional keyword arguments, including 'site'
        """
        super().__init__(fail_silently=fail_silently)
        self.site: Site | None = kwargs.get("site", None)

    def send_messages(self, email_messages: Sequence[EmailMessage]) -> int:
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.

        Args:
            email_messages: List of Django EmailMessage objects to send

        Returns:
            Number of successfully sent emails
        """
        if not email_messages:
            return 0

        num_sent = 0
        for message in email_messages:
            try:
                sent = self._send(message)
                if sent:
                    num_sent += 1
            except Exception:
                if not self.fail_silently:
                    raise
        return num_sent

    def _send(self, email_message: EmailMessage) -> bool:
        """
        Send an EmailMessage object.

        Args:
            email_message: Django EmailMessage object to send

        Returns:
            True if sent successfully, False otherwise
        """
        if not email_message.recipients():
            return False

        # Get the first recipient (ForwardEmail API sends to one recipient at a time)
        to_email = email_message.to[0]

        # Get site from connection or instance
        site = None
        if hasattr(email_message, "connection") and hasattr(
            email_message.connection, "site"
        ):
            site = email_message.connection.site
        else:
            site = self.site

        if not site:
            raise ValueError("Either request or site must be provided")

        # Import here to avoid import-time Django configuration issues
        from .models import EmailConfiguration

        # Get the site's email configuration
        try:
            config = EmailConfiguration.objects.get(site=site)
        except EmailConfiguration.DoesNotExist as e:
            raise ValueError(
                f"Email configuration not found for site: {site.domain}"
            ) from e

        # Get the from email, falling back to site's default if not provided
        from_email = None
        if email_message.from_email:
            from_email = sanitize_address(
                email_message.from_email, email_message.encoding
            )
        else:
            from_email = f"{config.from_name} <{config.from_email}>"

        # Extract clean email address if needed
        if from_email and "<" in from_email:
            from_email = ForwardEmailService.extract_email(from_email)

        # Get reply-to from message headers or use default
        reply_to = None
        if hasattr(email_message, "reply_to") and email_message.reply_to:
            reply_to = email_message.reply_to[0]
        elif (
            hasattr(email_message, "extra_headers")
            and email_message.extra_headers
            and "Reply-To" in email_message.extra_headers
        ):
            reply_to = email_message.extra_headers["Reply-To"]

        # Determine if we have HTML content
        html_content = None
        text_content = email_message.body

        # Check if this is a multipart message with HTML
        if (
            isinstance(email_message, EmailMultiAlternatives)
            and email_message.alternatives
        ):
            for content, content_type in email_message.alternatives:
                if content_type == "text/html":
                    html_content = str(content)
                    break

        try:
            ForwardEmailService.send_email(
                to=to_email,
                subject=str(email_message.subject),
                text=str(text_content),
                html=html_content,
                from_email=from_email,
                reply_to=reply_to,
                site=site,
            )
            return True
        except Exception:
            if not self.fail_silently:
                raise
            return False
