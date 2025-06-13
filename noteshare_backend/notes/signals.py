# notes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify
from .models import Like, StarRating, Comment, Note
from django.conf import settings
from django.contrib.auth import get_user_model 
from django.template.loader import render_to_string
from users.utils import send_email_sync
from .models import Like, StarRating, Comment, Note
from django.contrib.auth import get_user_model

import logging

logger = logging.getLogger(__name__)
User = get_user_model()

@receiver(post_save, sender=Like)
def send_like_notification(sender, instance, created, **kwargs):
    if created:
        note_owner = instance.note.uploader
        liker = instance.user

        if note_owner and liker and note_owner != liker:
            notify.send(
                sender=liker,
                recipient=note_owner,
                verb='liked',
                action_object=instance.note,
                description=f'{liker.username} liked your note: "{instance.note.title}"'
            )
            logger.info(f"Notification: {liker.username} liked {note_owner.username}'s note '{instance.note.title}'")

# StarRating এর জন্য নোটিফিকেশন
@receiver(post_save, sender=StarRating)
def send_star_rating_notification(sender, instance, created, **kwargs):
    if created:
        note_owner = instance.note.uploader
        rater = instance.user

        if note_owner and rater and note_owner != rater:
            notify.send(
                sender=rater,
                recipient=note_owner,
                verb='rated',
                action_object=instance.note, # StarRating অবজেক্টকে action_object হিসেবে না দিয়ে Note কে দিতে পারেন
                target=instance.note,
                description=f'{rater.username} rated your note: "{instance.note.title}" with {instance.stars} stars.'
            )
            logger.info(f"Notification: {rater.username} rated {note_owner.username}'s note '{instance.note.title}' with {instance.stars} stars.")

# Comment এর জন্য নোটিফিকেশন
@receiver(post_save, sender=Comment)
def send_comment_notification(sender, instance, created, **kwargs):
    if created:
        note_owner = instance.note.uploader
        commenter = instance.user

        if note_owner and commenter and note_owner != commenter:
            notify.send(
                sender=commenter,
                recipient=note_owner,
                verb='commented on',
                action_object=instance,
                target=instance.note,
                description=f'{commenter.username} commented on your note: "{instance.note.title}"'
            )
            logger.info(f"Notification: {commenter.username} commented on {note_owner.username}'s note '{instance.note.title}'. Comment: {instance.text[:50]}...")




@receiver(post_save, sender=Note)
def send_note_approval_notification(sender, instance, created, **kwargs):
    if not created and instance.is_approved:
        try:
            old_instance = Note.objects.get(pk=instance.pk)
            if not old_instance.is_approved and instance.is_approved:
                note_uploader = instance.uploader

                if note_uploader and note_uploader.email:
                    # ইমেইল নোটিফিকেশন
                    email_subject = 'Your Note Has Been Approved!'
                    context = {
                        'user': note_uploader,
                        'note': instance,
                        'frontend_url': settings.FRONTEND_URL,
                        'note_detail_url': f"{settings.FRONTEND_URL}/notes/{instance.id}/"
                    }

                    plain_message = render_to_string('notes/emails/note_approved_email.txt', context)
                    html_message = render_to_string('notes/emails/note_approved_email.html', context)

                    # === এখানে পরিবর্তন: synchronousভাবে ইমেইল পাঠান ===
                    if send_email_sync(
                        subject=email_subject,
                        plain_message=plain_message,
                        html_message=html_message,
                        recipient_email=note_uploader.email
                    ):
                        logger.info(f"Note approval email sent synchronously to {note_uploader.username} for note: {instance.title}")
                    else:
                        logger.error(f"Failed to send note approval email synchronously to {note_uploader.username} for note: {instance.title}")

                    # ইন-অ্যাপ নোটিফিকেশন (django-notifications)
                    # django-notifications এর `notify.send` ফাংশনটি inherently synchronous।
                    # তাই এখানে কোনো `.delay()` প্রয়োজন নেই, সরাসরি কল করুন।
                    notify.send(
                        sender=note_uploader, # নোটিফিকেশনের প্রেরক
                        recipient=note_uploader, # নোটিফিকেশন প্রাপক
                        verb='approved',
                        action_object=instance, # Note অবজেক্টকে action_object হিসেবে দিন
                        target=instance, # Note অবজেক্টকে target হিসেবে দিন
                        description=f'Your note "{instance.title}" has been approved and is now visible to others.'
                    )
                    logger.info(f"Note approval in-app notification sent synchronously for {note_uploader.username} for note: {instance.title}")

        except Note.DoesNotExist:
            logger.error(f"Error finding old note instance with ID {instance.pk} during approval notification.")
        except Exception as e:
            logger.error(f"Error sending note approval notifications synchronously for note {instance.id}: {e}", exc_info=True)