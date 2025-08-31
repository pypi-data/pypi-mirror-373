"""
Tests for django-forwardemail models.
"""

import pytest
from django.contrib.sites.models import Site
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from django_forwardemail.models import EmailConfiguration


@pytest.mark.django_db
class TestEmailConfiguration:
    """Test cases for EmailConfiguration model."""

    def test_create_email_configuration(self):
        """Test creating a basic email configuration."""
        site = Site.objects.get_current()
        config = EmailConfiguration.objects.create(
            site=site,
            api_key='test-api-key',
            from_email='test@example.com',
            from_name='Test Sender',
            reply_to='reply@example.com',
        )

        assert config.site == site
        assert config.api_key == 'test-api-key'
        assert config.from_email == 'test@example.com'
        assert config.from_name == 'Test Sender'
        assert config.reply_to == 'reply@example.com'
        assert config.created_at is not None
        assert config.updated_at is not None

    def test_string_representation(self):
        """Test the string representation of EmailConfiguration."""
        site = Site.objects.get_current()
        config = EmailConfiguration.objects.create(
            site=site,
            api_key='test-api-key',
            from_email='test@example.com',
            from_name='Test Sender',
            reply_to='reply@example.com',
        )

        expected = f"Test Sender <test@example.com> ({site.domain})"
        assert str(config) == expected

    def test_unique_site_constraint(self):
        """Test that only one configuration per site is allowed."""
        site = Site.objects.get_current()

        # Create first configuration
        EmailConfiguration.objects.create(
            site=site,
            api_key='test-api-key-1',
            from_email='test1@example.com',
            from_name='Test Sender 1',
            reply_to='reply1@example.com',
        )

        # Try to create second configuration for same site
        with pytest.raises(IntegrityError):
            EmailConfiguration.objects.create(
                site=site,
                api_key='test-api-key-2',
                from_email='test2@example.com',
                from_name='Test Sender 2',
                reply_to='reply2@example.com',
            )

    def test_email_field_validation(self):
        """Test email field validation."""
        site = Site.objects.get_current()

        # Test invalid from_email
        config = EmailConfiguration(
            site=site,
            api_key='test-api-key',
            from_email='invalid-email',
            from_name='Test Sender',
            reply_to='reply@example.com',
        )

        with pytest.raises(ValidationError):
            config.full_clean()

    def test_multiple_sites(self):
        """Test configurations for multiple sites."""
        # Create additional site
        site1 = Site.objects.get_current()
        site2 = Site.objects.create(domain='site2.example.com', name='Site 2')

        # Create configurations for both sites
        config1 = EmailConfiguration.objects.create(
            site=site1,
            api_key='test-api-key-1',
            from_email='test1@example.com',
            from_name='Test Sender 1',
            reply_to='reply1@example.com',
        )

        config2 = EmailConfiguration.objects.create(
            site=site2,
            api_key='test-api-key-2',
            from_email='test2@example.com',
            from_name='Test Sender 2',
            reply_to='reply2@example.com',
        )

        assert config1.site == site1
        assert config2.site == site2
        assert EmailConfiguration.objects.count() == 2
