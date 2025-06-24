# users/utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_email_sync(subject, plain_message, html_message, recipient_email):
    try:
        email_obj = EmailMultiAlternatives(
            subject=subject,
            body=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[recipient_email]
        )
        email_obj.attach_alternative(html_message, "text/html")
        email_obj.send(fail_silently=False)
        logger.info(f"Successfully sent email synchronously to {recipient_email} with subject: {subject}")
        return True
    except Exception as e:
        logger.error(f"Failed to send email synchronously to {recipient_email} with subject: {subject}: {e}", exc_info=True)
        return False

