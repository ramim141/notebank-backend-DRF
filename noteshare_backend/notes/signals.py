from django.db.models.signals import post_save 
from django.dispatch import receiver 
from notifications.signals import notify 
from .models import Like, Rating, Note 
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


@receiver(post_save, sender=Rating) # যখনই একটি Rating অবজেক্ট সেভ হবে
def send_rating_comment_notification(sender, instance, created, **kwargs):
    
    if created:
        note_owner = instance.note.uploader
        commenter = instance.user

        if note_owner and commenter and note_owner != commenter:
            verb_text = 'rated'
            description_text = f'{commenter.username} rated your note: "{instance.note.title}"'
            if instance.comment and instance.comment.strip(): 
                verb_text = 'commented on'
                description_text = f'{commenter.username} commented on your note: "{instance.note.title}"'
            
            notify.send(
                sender=commenter,
                recipient=note_owner,
                verb=verb_text,
                action_object=instance, 
                target=instance.note,   
                description=description_text
            )
            print(f"Notification: {commenter.username} {verb_text} {note_owner.username}'s note '{instance.note.title}'")