from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid 
from django.core.validators import RegexValidator


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
    department = models.CharField(max_length=100, blank=True, null=True, help_text="User's primary department")
    
    def __str__(self):
        return self.username