# notes/signals.py

from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from .models import Note, StarRating, Contributor

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
def rating_saved(sender, instance, **kwargs):
    update_contributor_stats(instance.note.uploader)

@receiver(post_delete, sender=StarRating)
def rating_deleted(sender, instance, **kwargs):
    update_contributor_stats(instance.note.uploader)