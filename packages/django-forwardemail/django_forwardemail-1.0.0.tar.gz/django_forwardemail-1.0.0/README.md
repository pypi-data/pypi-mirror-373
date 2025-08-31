# Django ForwardEmail

A Django package for integrating with the [ForwardEmail](https://forwardemail.net) API service, providing multi-site email configuration and Django email backend support.

## Features

- **Multi-site Support**: Configure different ForwardEmail settings for each Django site
- **Django Email Backend**: Drop-in replacement for Django's default email backend
- **Service Class**: Direct API integration for custom email sending logic
- **Admin Interface**: User-friendly Django admin interface for managing configurations
- **Type Safety**: Full type hints and mypy compatibility
- **Comprehensive Logging**: Debug-friendly logging for troubleshooting

## Requirements

- Python 3.10+
- Django 4.2+

## Installation

```bash
pip install django-forwardemail
```

## Quick Start

### 1. Add to Django Settings

Add `django_forwardemail` to your `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ... other apps
    'django.contrib.sites',  # Required for multi-site support
    'django_forwardemail',
]

# Optional: Set ForwardEmail as your default email backend
EMAIL_BACKEND = 'django_forwardemail.backends.ForwardEmailBackend'

# Optional: Configure ForwardEmail API base URL (defaults to https://api.forwardemail.net)
FORWARD_EMAIL_BASE_URL = 'https://api.forwardemail.net'
```

### 2. Run Migrations

```bash
python manage.py migrate django_forwardemail
```

### 3. Configure in Django Admin

1. Go to Django Admin → Sites → Sites and ensure you have your site configured
2. Go to Django Admin → Django ForwardEmail → Email Configurations
3. Create a new configuration with:
   - **Site**: Select your site
   - **API Key**: Your ForwardEmail API key
   - **From Email**: Default sender email address
   - **From Name**: Default sender name
   - **Reply To**: Default reply-to address

## Usage

### Using Django's Email System

Once configured, you can use Django's standard email functions:

```python
from django.core.mail import send_mail, EmailMultiAlternatives

# Simple text email
send_mail(
    'Subject here',
    'Here is the message.',
    'from@example.com',
    ['to@example.com'],
    fail_silently=False,
)

# HTML email with text fallback
msg = EmailMultiAlternatives(
    'Subject here',
    'Plain text version of the message.',
    'from@example.com',
    ['to@example.com']
)
msg.attach_alternative('<h1>HTML version</h1><p>of the message.</p>', "text/html")
msg.send()
```

### Using the Service Class Directly

For more control, use the `ForwardEmailService` directly:

```python
from django_forwardemail.services import ForwardEmailService
from django.contrib.sites.models import Site

# Get the current site
site = Site.objects.get_current()

# Send simple text email
response = ForwardEmailService.send_email(
    to='recipient@example.com',
    subject='Test Email',
    text='This is a test email.',
    site=site,
)

# Send HTML email with text fallback
response = ForwardEmailService.send_email(
    to='recipient@example.com',
    subject='HTML Test Email',
    text='This is the plain text version.',
    html='<h1>HTML Email</h1><p>This is a <strong>test</strong> email.</p>',
    site=site,
)

# Send with custom from/reply-to
response = ForwardEmailService.send_email(
    to='recipient@example.com',
    subject='Custom Sender Email',
    text='This email has custom sender info.',
    from_email='custom@example.com',
    reply_to='support@example.com',
    site=site,
)
```

### Using in Django Views

Here's how to integrate email sending in your Django views:

```python
from django.shortcuts import render
from django.contrib import messages
from django.http import HttpResponseRedirect
from django_forwardemail.services import ForwardEmailService
from django.contrib.sites.shortcuts import get_current_site

def contact_view(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        try:
            # Send notification email
            ForwardEmailService.send_email(
                to='admin@example.com',
                subject=f'Contact Form: {name}',
                text=f'From: {name} <{email}>\n\nMessage:\n{message}',
                html=f'''
                <h2>Contact Form Submission</h2>
                <p><strong>From:</strong> {name} &lt;{email}&gt;</p>
                <p><strong>Message:</strong></p>
                <p>{message}</p>
                ''',
                reply_to=email,
                request=request,  # Automatically detects site
            )
            
            messages.success(request, 'Your message has been sent!')
            return HttpResponseRedirect('/contact/')
            
        except Exception as e:
            messages.error(request, f'Failed to send message: {str(e)}')
    
    return render(request, 'contact.html')
```

### Template-based Emails

For complex emails, use Django templates:

```python
from django.template.loader import render_to_string
from django_forwardemail.services import ForwardEmailService

def send_welcome_email(user, request):
    # Render email templates
    text_content = render_to_string('emails/welcome.txt', {
        'user': user,
        'site_name': 'Your Site',
    })
    
    html_content = render_to_string('emails/welcome.html', {
        'user': user,
        'site_name': 'Your Site',
    })
    
    # Send email
    ForwardEmailService.send_email(
        to=user.email,
        subject='Welcome to Your Site!',
        text=text_content,
        html=html_content,
        request=request,
    )
```

### Async Email Sending with Celery

For high-volume applications, use Celery for async email sending:

```python
from celery import shared_task
from django_forwardemail.services import ForwardEmailService
from django.contrib.sites.models import Site

@shared_task
def send_email_async(to, subject, text, html=None, site_id=1):
    """Send email asynchronously using Celery."""
    try:
        site = Site.objects.get(id=site_id)
        ForwardEmailService.send_email(
            to=to,
            subject=subject,
            text=text,
            html=html,
            site=site,
        )
        return f"Email sent successfully to {to}"
    except Exception as e:
        return f"Failed to send email: {str(e)}"

# Usage in views
def some_view(request):
    # Queue email for background processing
    send_email_async.delay(
        to='user@example.com',
        subject='Background Email',
        text='This email was sent in the background.',
        site_id=request.site.id,
    )
```

### Multi-site Configuration

For multi-site setups, create separate `EmailConfiguration` objects for each site:

```python
from django.contrib.sites.models import Site
from django_forwardemail.models import EmailConfiguration

# Configure for site 1
site1 = Site.objects.get(domain='site1.example.com')
EmailConfiguration.objects.create(
    site=site1,
    api_key='your-api-key-1',
    from_email='noreply@site1.example.com',
    from_name='Site 1',
    reply_to='support@site1.example.com',
)

# Configure for site 2
site2 = Site.objects.get(domain='site2.example.com')
EmailConfiguration.objects.create(
    site=site2,
    api_key='your-api-key-2',
    from_email='noreply@site2.example.com',
    from_name='Site 2',
    reply_to='support@site2.example.com',
)
```

## API Reference

### ForwardEmailService

#### `send_email(**kwargs)`

Send an email through the ForwardEmail API.

**Parameters:**
- `to` (str): Recipient email address
- `subject` (str): Email subject line
- `text` (str): Plain text email content
- `from_email` (str, optional): Sender email address (uses config default if not provided)
- `html` (str, optional): HTML email content
- `reply_to` (str, optional): Reply-to email address (uses config default if not provided)
- `request` (HttpRequest, optional): Django request object for site detection
- `site` (Site, optional): Django Site object (auto-detected if not provided)
- `base_url` (str, optional): ForwardEmail API base URL

**Returns:**
- `Dict[str, Any]`: API response from ForwardEmail

**Raises:**
- `ImproperlyConfigured`: If site configuration is missing
- `Exception`: If email sending fails

### EmailConfiguration Model

Django model for storing ForwardEmail configurations per site.

**Fields:**
- `site`: ForeignKey to Django Site
- `api_key`: ForwardEmail API key
- `from_email`: Default sender email address
- `from_name`: Default sender name
- `reply_to`: Default reply-to address
- `created_at`: Timestamp when created
- `updated_at`: Timestamp when last updated

## Settings

### `FORWARD_EMAIL_BASE_URL`

**Default:** `'https://api.forwardemail.net'`

The base URL for the ForwardEmail API. You typically don't need to change this unless you're using a custom ForwardEmail instance.

### `EMAIL_BACKEND`

Set this to `'django_forwardemail.backends.ForwardEmailBackend'` to use ForwardEmail as your default email backend.

## Development

### Running Tests

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=django_forwardemail
```

### Code Quality

```bash
# Format code
black django_forwardemail/

# Lint code
flake8 django_forwardemail/

# Type checking
mypy django_forwardemail/
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests for your changes
5. Ensure all tests pass
6. Commit your changes (`git commit -m 'Add amazing feature'`)
7. Push to the branch (`git push origin feature/amazing-feature`)
8. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Support

- **Documentation**: [https://django-forwardemail.readthedocs.io/](https://django-forwardemail.readthedocs.io/)
- **Issues**: [https://github.com/thrillwiki/django-forwardemail/issues](https://github.com/thrillwiki/django-forwardemail/issues)
- **ForwardEmail Documentation**: [https://forwardemail.net/docs](https://forwardemail.net/docs)

## Changelog

### 1.0.0 (2025-08-30)

- **STABLE RELEASE** - Production-ready ForwardEmail integration
- Multi-site email configuration support with automatic site detection
- Django email backend integration with full compatibility
- ForwardEmail API service class with comprehensive error handling
- Django admin interface for easy configuration management
- Full backward compatibility with existing Django email patterns
- Comprehensive test suite covering Django 4.2+ and Python 3.10+
- Modern type hints and logging integration
- Extensive documentation and usage examples
- Automated CI/CD pipeline with PyPI publishing
