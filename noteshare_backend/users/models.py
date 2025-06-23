from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid 
from django.core.validators import RegexValidator
from taggit.managers import TaggableManager
from notes.models import Department

GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
   
    ]

def user_profile_picture_path(instance, filename):
    return f'profile_pics/user_{instance.id}/{filename}'



class User(AbstractUser):
    is_email_verified = models.BooleanField(default=False)
    email_verification_token = models.UUIDField(default=uuid.uuid4, editable=False, null=True, blank=True)
    
    profile_picture = models.ImageField(
        upload_to=user_profile_picture_path,
        null=True,                           
        blank=True                          
    )
    student_id_validator = RegexValidator(
        regex=r'^\d{3}-\d{3}-\d{3}$', 
        message="Student ID must be in the format: 'XXX-XXX-XXX' (e.g., 222-115-141)."
    )
    student_id = models.CharField(
        max_length=11, 
        validators=[student_id_validator],
        unique=True, 
        null=False,   
        blank=False,  

    )
    # department = models.ForeignKey(
    #     Department, 
    #     on_delete=models.SET_NULL, 
    #     null=True, 
    #     blank=True,
    #     related_name='users',
    #     help_text="User's primary department"
    # )
    department = models.CharField(max_length=100, blank=True, null=True, help_text="User's primary department")
    batch = models.CharField(max_length=20, blank=True, null=True)
    section = models.CharField(max_length=10, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True, help_text="A short biography about the user.")
    mobile_number_validator = RegexValidator(
        regex=r'^\+?(\d{1,3})?\d{9,15}$', 
        message="Mobile number must be entered in the format: '+999999999' or '017XXXXXXXXX'. Up to 15 digits allowed, optional country code."
    )
    mobile_number = models.CharField(
        validators=[mobile_number_validator],
        max_length=17, 
        blank=True,
        null=True,
        unique=False 
    )
    university = models.CharField(max_length=255, blank=True, null=True)
    website = models.URLField(max_length=255, blank=True, null=True, help_text="Personal or professional website URL.")
    birthday = models.DateField(blank=True, null=True)
    gender = models.CharField(max_length=100, choices=GENDER_CHOICES, blank=True, null=True)
    skills = TaggableManager(blank=True, help_text="A comma-separated list of skills (e.g., Python, Django, React).")
    
    def __str__(self):
        return self.username