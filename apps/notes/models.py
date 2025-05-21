# notes/models.py

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True, blank=True)

    def __str__(self):
        return self.name


class Note(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notes')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    course_name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    file = models.FileField(upload_to='notes/')
    upload_date = models.DateTimeField(auto_now_add=True)
    
    download_count = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.title


class NoteRating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='ratings')
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])  # 1 to 5

    class Meta:
        unique_together = ('user', 'note')


class NoteComment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='comments')
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
