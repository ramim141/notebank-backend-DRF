from django.db import models
from django.conf import settings 
from django.core.validators import MinValueValidator, MaxValueValidator 
from taggit.managers import TaggableManager


def note_file_path(instance, filename):
    return f'notes/user_{instance.uploader.id}/{filename}' 

class Note(models.Model):
    uploader = models.ForeignKey(
         settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='uploaded_notes'
        # null=True, blank=True 
    )   
    
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    

    file = models.FileField(upload_to=note_file_path) 
    

    course_name = models.CharField(max_length=100, blank=True, null=True) 
    department_name = models.CharField(max_length=100, blank=True, null=True)
    semester = models.CharField(max_length=50, blank=True, null=True) 
    tags = TaggableManager(blank=True)
    download_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


    @property
    def average_rating(self):
        all_ratings = self.note_ratings.all() 
        if all_ratings.exists():
            return round(sum(r.stars for r in all_ratings) / all_ratings.count(), 2)
        return 0.0

class Rating(models.Model):
    note = models.ForeignKey(
        Note, 
        on_delete=models.CASCADE, 
        related_name='note_ratings'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE,
        related_name='given_ratings'
    )
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)] 
    )
    comment = models.TextField(blank=True, null=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('note', 'user') 
        ordering = ['-created_at'] 

    def __str__(self):
        return f"{self.stars} stars for '{self.note.title}' by {self.user.username}"


class Like(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='liked_notes' 
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='likes' 
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
   
        unique_together = ('user', 'note')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} likes {self.note.title}"


class Bookmark(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='bookmarked_notes' 
    )
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='bookmarks' 
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
      
        unique_together = ('user', 'note')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.user.username} bookmarked {self.note.title}"