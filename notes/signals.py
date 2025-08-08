# notes/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from .models import Note, StarRating, Comment, Contributor, NoteRequest, Notification 
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.contrib.contenttypes.models import ContentType
import json
import logging

logger = logging.getLogger(__name__)

User = get_user_model()

def update_contributor_stats(user):
    if not user:
        return
    approved_notes = Note.objects.filter(uploader=user, is_approved=True)
    note_count = approved_notes.count()
    avg_rating_data = approved_notes.aggregate(avg_stars=Avg('star_ratings__stars'))
    avg_rating = avg_rating_data['avg_stars'] if avg_rating_data['avg_stars'] is not None else 0.0

    contributor_profile, created = Contributor.objects.update_or_create(
        user=user,
        defaults={
            'note_contribution_count': note_count,
            'average_star_rating': round(avg_rating, 2)
        }
    )

    if note_count == 0:
        contributor_profile.delete()


@receiver(post_save, sender=Note)
def note_saved_or_approved(sender, instance, created, **kwargs):
    update_contributor_stats(instance.uploader)

@receiver(post_delete, sender=Note)
def note_deleted(sender, instance, **kwargs):
    update_contributor_stats(instance.uploader)

@receiver(post_save, sender=StarRating)
def rating_saved(sender, instance, created, **kwargs):
    update_contributor_stats(instance.note.uploader)
    # Notify note owner when someone rates their note (avoid self-notify)
    try:
        if created and instance.user_id != instance.note.uploader_id:
            Notification.objects.create(
                actor_content_type=ContentType.objects.get_for_model(instance.user),
                actor_object_id=instance.user.pk,
                verb=f"rated your note ({instance.stars}★)",
                target_content_type=ContentType.objects.get_for_model(instance.note),
                target_object_id=instance.note.pk,
            )
            send_notification_broadcast(Notification.objects.latest('id'))
    except Exception as e:
        logger.debug(f"Rating notification skipped: {e}")


@receiver(post_delete, sender=StarRating)
def rating_deleted(sender, instance, **kwargs):
    update_contributor_stats(instance.note.uploader)
    


def send_notification_broadcast(notification, extra: dict | None = None):
    try:
        channel_layer = get_channel_layer()
        if not channel_layer:
            logger.debug("Channels layer not configured; skipping notification broadcast.")
            return
        notification_data = {
            'id': notification.id,
            'actor': str(notification.actor),
            'verb': notification.verb,
            'target': str(notification.target) if notification.target else None,
            'timestamp': notification.timestamp.isoformat(),
            'target_url': f"/notes/{notification.target.id}" if notification.target and isinstance(notification.target, Note) else f"/note-requests",
            'visibility': 'global',
        }
        if extra:
            notification_data.update(extra)
        async_to_sync(channel_layer.group_send)(
            'notifications_group', 
            {
                'type': 'broadcast_notification', 
                'message': notification_data
            }
        )
    except Exception as e:
        logger.warning(f"Skipping notification broadcast due to error: {e}")


@receiver(post_save, sender=NoteRequest)
def note_request_created(sender, instance, created, **kwargs):
    if created:
        try:
            notification = Notification.objects.create(
                actor_content_type=ContentType.objects.get_for_model(instance.user),
                actor_object_id=instance.user.pk,
                verb='requested a note',
                target_content_type=ContentType.objects.get_for_model(instance),
                target_object_id=instance.pk,
            )
            # Broadcast to all users (global group)
            send_notification_broadcast(notification)
        except Exception as e:
            logger.warning(f"Failed to create/broadcast notification for NoteRequest: {e}")


def send_notification_to_user(user_id: int, notification: Notification):
    # Fallback to global broadcast with recipient hint so clients can filter
    send_notification_broadcast(notification, extra={'recipient_user_id': user_id, 'visibility': 'user'})


@receiver(post_save, sender=Note)
def note_approved_or_created(sender, instance, created, **kwargs):
    update_fields = kwargs.get('update_fields') or []

    # Only when approved
    if not instance.is_approved:
        return

    # Avoid duplicate notifications for the same note approval
    try:
        approval_exists = Notification.objects.filter(
            verb='your note was approved',
            target_content_type=ContentType.objects.get_for_model(instance),
            target_object_id=instance.pk,
        ).exists()
    except Exception:
        approval_exists = False

    # Trigger when:
    # - created and already approved, or
    # - 'is_approved' explicitly updated, or
    # - no prior approval notification exists (covers admin saves with update_fields=None)
    if created or ('is_approved' in update_fields) or (not approval_exists):
        try:
            notification = Notification.objects.create(
                actor_content_type=ContentType.objects.get_for_model(instance.uploader),
                actor_object_id=instance.uploader.pk,
                verb='your note was approved',
                target_content_type=ContentType.objects.get_for_model(instance),
                target_object_id=instance.pk,
            )
            send_notification_to_user(instance.uploader_id, notification)
        except Exception as e:
            logger.warning(f"Failed to create/send approval notification for Note: {e}")


@receiver(post_save, sender=Note)
def note_created_pending(sender, instance, created, **kwargs):
    if created and not instance.is_approved:
        try:
            Notification.objects.create(
                actor_content_type=ContentType.objects.get_for_model(instance.uploader),
                actor_object_id=instance.uploader.pk,
                verb='uploaded a new note (pending approval)',
                target_content_type=ContentType.objects.get_for_model(instance),
                target_object_id=instance.pk,
            )
        except Exception as e:
            logger.warning(f"Failed to create pending notification for Note: {e}")
        else:
            try:
                send_notification_broadcast(Notification.objects.latest('id'))
            except Exception as e:
                logger.debug(f"Broadcast skipped/failed after pending Note notification: {e}")


@receiver(post_save, sender=Comment)
def comment_saved(sender, instance, created, **kwargs):
    # Notify note owner when someone comments on their note (avoid self-notify)
    try:
        if created and instance.user_id != instance.note.uploader_id:
            Notification.objects.create(
                actor_content_type=ContentType.objects.get_for_model(instance.user),
                actor_object_id=instance.user.pk,
                verb="commented on your note",
                target_content_type=ContentType.objects.get_for_model(instance.note),
                target_object_id=instance.note.pk,
            )
            send_notification_broadcast(Notification.objects.latest('id'))
    except Exception as e:
        logger.debug(f"Comment notification skipped: {e}")