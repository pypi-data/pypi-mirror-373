import base64
import logging
from typing import TYPE_CHECKING, Any, Optional

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.mail.message import sanitize_address
from django.http import HttpRequest

if TYPE_CHECKING:
    from django.contrib.sites.models import Site

logger = logging.getLogger(__name__)


class ForwardEmailService:
    """
    Service class for sending emails through the ForwardEmail API.

    This service handles authentication, email formatting, and API communication
    with the ForwardEmail service, with support for multi-site configurations.
    """

    DEFAULT_BASE_URL = "https://api.forwardemail.net"

    @classmethod
    def send_email(
        cls,
        *,
        to: str,
        subject: str,
        text: str,
        from_email: str | None = None,
        html: str | None = None,
        reply_to: str | None = None,
        request: HttpRequest | None = None,
        site: Optional["Site"] = None,
        base_url: str | None = None,
    ) -> dict[str, Any]:
        """
        Send an email through the ForwardEmail API.

        Args:
            to: Recipient email address
            subject: Email subject line
            text: Plain text email content
            from_email: Sender email address (optional, uses config default)
            html: HTML email content (optional)
            reply_to: Reply-to email address (optional, uses config default)
            request: Django request object for site detection (optional)
            site: Django Site object (optional, auto-detected if not provided)
            base_url: ForwardEmail API base URL (optional, uses default)

        Returns:
            Dict containing the API response

        Raises:
            ImproperlyConfigured: If site configuration is missing
            Exception: If email sending fails
        """
        # Import Django models here to avoid import-time configuration issues
        from django.contrib.sites.models import Site
        from django.contrib.sites.shortcuts import get_current_site

        from .models import EmailConfiguration

        # Get the site configuration
        if site is None and request is not None:
            site_obj = get_current_site(request)
            # Ensure we have a proper Site object, not RequestSite
            if hasattr(site_obj, "pk") and isinstance(site_obj, Site):
                site = site_obj
            else:
                raise ImproperlyConfigured("Could not determine site from request")
        elif site is None:
            # Try to get the default site if no site or request provided
            try:
                site = Site.objects.get_current()
            except Site.DoesNotExist:
                # Fall back to the first site
                try:
                    site = Site.objects.first()
                    if site is None:
                        raise ImproperlyConfigured(
                            "No sites configured. Please create a Site object."
                        )
                except Exception as e:
                    raise ImproperlyConfigured(
                        "Could not determine site. Please provide either 'request' or 'site' parameter, "
                        "or ensure at least one Site object exists in the database."
                    ) from e

        try:
            # Fetch the email configuration for the current site
            email_config = EmailConfiguration.objects.get(site=site)
            api_key = email_config.api_key

            # Use provided from_email or construct from config
            if not from_email:
                from_email = f"{email_config.from_name} <{email_config.from_email}>"
            elif "<" not in from_email:
                # If from_email is provided but doesn't include a name, add the
                # configured name
                from_email = f"{email_config.from_name} <{from_email}>"

            # Use provided reply_to or fall back to config
            if not reply_to:
                reply_to = email_config.reply_to

        except EmailConfiguration.DoesNotExist as e:
            site_domain = site.domain if site else "unknown"
            raise ImproperlyConfigured(
                f"Email configuration is missing for site: {site_domain}"
            ) from e

        # Ensure the reply_to address is clean
        if reply_to:
            reply_to = sanitize_address(reply_to, "utf-8")

        # Format data for the API
        data = {
            "from": from_email,
            "to": to,
            "subject": subject,
            "text": text,
            "replyTo": reply_to,
        }

        # Add HTML version if provided
        if html:
            data["html"] = html

        # Get base URL from settings or use default
        api_base_url = base_url or getattr(
            settings, "FORWARD_EMAIL_BASE_URL", cls.DEFAULT_BASE_URL
        )

        # Log debug information if debug mode is enabled
        if getattr(settings, "DEBUG", False):
            site_domain = site.domain if site else "unknown"
            logger.debug(
                "ForwardEmail API Request - From: %s, To: %s, Reply-To: %s, Site: %s",
                from_email,
                to,
                reply_to,
                site_domain,
            )

        # Create Basic auth header with API key as username and empty password
        auth_header = base64.b64encode(f"{api_key}:".encode()).decode()
        headers = {
            "Authorization": f"Basic {auth_header}",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        try:
            response = requests.post(
                f"{api_base_url}/v1/emails",
                json=data,
                headers=headers,
                timeout=60,
            )

            # Log response details in debug mode
            if getattr(settings, "DEBUG", False):
                logger.debug(
                    "ForwardEmail API Response - Status: %s, Body: %s",
                    response.status_code,
                    response.text,
                )

            if response.status_code != 200:
                error_message = response.text if response.text else "Unknown error"
                raise Exception(
                    f"Failed to send email (Status {response.status_code}): "
                    f"{error_message}"
                )

            return response.json()

        except requests.RequestException as e:
            logger.error("ForwardEmail API request failed: %s", str(e))
            raise Exception(f"Failed to send email: {str(e)}") from e
        except Exception as e:
            logger.error("ForwardEmail service error: %s", str(e))
            raise Exception(f"Failed to send email: {str(e)}") from e

    @staticmethod
    def extract_email(email_string: str) -> str:
        """
        Extract clean email address from a string that may contain a name.

        Args:
            email_string: Email string like "Name <email@domain.com>" or
                         "email@domain.com"

        Returns:
            Clean email address
        """
        if "<" in email_string and ">" in email_string:
            # Extract email from "Name <email@domain.com>" format
            start = email_string.find("<") + 1
            end = email_string.find(">")
            return email_string[start:end].strip()
        return email_string.strip()


# Backward compatibility alias
EmailService = ForwardEmailService
