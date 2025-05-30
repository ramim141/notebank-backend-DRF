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
    DEPARTMENT_CHOICES = [
        ('CSE', 'Computer Science and Engineering'),
        ('EEE', 'Electrical and Electronic Engineering'),
        ('BBA', 'Bachelor of Business Administration'),
        ('SWE', 'Software Engineering'),
        ('Civil', 'Civil Engineering'),
        ('Architecture', 'Architecture'),
        ('Textile', 'Textile Engineering'),
        ('Agriculture', 'Agriculture'),
        ('ENG', 'English'),
        ('ECN', 'Economics'),
        ('PHY', 'Physics'),
        ('ME', 'Mechanical Engineering'),
        ('CE', 'Civil Engineering'),
        ('IPE', 'Industrial and Production Engineering'),
        ('Other', 'Other')
    ]
    department_name = models.CharField(
        max_length=100, 
        choices=DEPARTMENT_CHOICES,
        blank=True, 
        null=True
    )
    semester = models.CharField(max_length=50, blank=True, null=True) 
    tags = TaggableManager(blank=True)
    download_count = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title


    @property
    def average_rating(self):
        # এখন StarRating মডেল থেকে গড় রেটিং গণনা করা হবে
        all_ratings = self.star_ratings.all() # related_name পরিবর্তন করা হয়েছে
        if all_ratings.exists():
            return round(sum(r.stars for r in all_ratings) / all_ratings.count(), 2)
        return 0.0

class StarRating(models.Model):
    note = models.ForeignKey(
        Note,
        on_delete=models.CASCADE,
        related_name='star_ratings' # নতুন related_name
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_star_ratings' # নতুন related_name
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
        related_name='comments' # নতুন related_name
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='given_comments' # নতুন related_name
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    class Meta:
        ordering = ['-created_at'] # এখানে unique_together নেই, তাই একাধিক কমেন্ট সম্ভব

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