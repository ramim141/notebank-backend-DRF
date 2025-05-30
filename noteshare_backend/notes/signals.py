# notes/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from notifications.signals import notify
# নতুন মডেলগুলি ইম্পোর্ট করুন
from .models import Like, StarRating, Comment, Note
from django.conf import settings

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
            print(f"Notification: {liker.username} liked {note_owner.username}'s note '{instance.note.title}'")

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
            print(f"Notification: {rater.username} rated {note_owner.username}'s note '{instance.note.title}' with {instance.stars} stars.")

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
                action_object=instance, # কমেন্ট অবজেক্টকে action_object হিসেবে দিতে পারেন
                target=instance.note,
                description=f'{commenter.username} commented on your note: "{instance.note.title}"'
            )
            print(f"Notification: {commenter.username} commented on {note_owner.username}'s note '{instance.note.title}'. Comment: {instance.text[:50]}...")