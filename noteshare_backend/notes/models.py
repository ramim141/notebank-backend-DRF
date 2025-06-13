from django.db import models
from django.conf import settings 
from django.core.validators import MinValueValidator, MaxValueValidator 
from taggit.managers import TaggableManager



def note_file_path(instance, filename):
    return f'notes/user_{instance.uploader.id}/{filename}' 


class Department(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

class Course(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')


    class Meta:
        unique_together = ('name', 'department')
        
        ordering = ['name']

    def __str__(self):
        return f'{self.department.name} - {self.name}'
    





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
    
    is_approved = models.BooleanField(default=False)

    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, blank=True, related_name='notes')
    
    semester = models.CharField(max_length=50, blank=True, null=True) 
    tags = TaggableManager(blank=True)
    download_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


    @property
    def average_rating(self):
    
        all_ratings = self.star_ratings.all() 
        if all_ratings.exists():
            return round(sum(r.stars for r in all_ratings) / all_ratings.count(), 2)
        return 0.0

class StarRating(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='star_ratings' 
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_star_ratings' 
    )
    stars = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('note', 'user') 
        ordering = ['-created_at'] 

    def __str__(self):
        return f"{self.stars} stars for '{self.note.title}' by {self.user.username}"

class Comment(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_comments'
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('note', 'user')

    def __str__(self):
        return f"Comment by {self.user.username} on '{self.note.title}': {self.text[:50]}..."



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