# users/utils.py

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

# এই ফাংশনটি আপনার existing send_auth_email (যদি থাকে) এর বিকল্প বা নতুন synchronous helper হিসেবে ব্যবহার করতে পারেন।
# যদি আপনার existing send_auth_email Celery ব্যবহার করে, তাহলে এটি একটি নতুন ফাংশন হিসেবে যোগ করুন।
# এটি ইমেইল পাঠানোর কাজটি সিঙ্ক্রোনাসভাবে করবে।
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

# আপনার যদি পূর্বে send_auth_email ফাংশন থাকে এবং সেটি Celery ব্যবহার করে, তাহলে সেটি অপরিবর্তিত রাখুন।
# যদি সেটিও synchronous হয়, তাহলে এই send_email_sync কে সেই ফাংশনের অংশ বানিয়ে নিতে পারেন।
# এখানে, আমরা ধরে নিচ্ছি send_email_sync একটি নতুন বা সংশোধিত synchronous ফাংশন।