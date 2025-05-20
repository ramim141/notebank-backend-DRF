from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
class UserManager(BaseUserManager):

    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        if not first_name:
            raise ValueError('The First Name field must be set')
        if not last_name:
            raise ValueError('The Last Name field must be set')
        
        email = self.normalize_email(email)
        user = self.model(email=email, first_name=first_name, last_name=last_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if not extra_fields.get('is_staff') or not extra_fields.get('is_superuser'):
            raise ValueError('Superuser must have is_staff=True and is_superuser=True.')
        
        return self.create_user(email, first_name, last_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        STUDENT = 'Student', _('Student')
        FACULTY = 'Faculty', _('Faculty')
        
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    
    # is_student = models.BooleanField(default=False)
    # is_faculty = models.BooleanField(default=False)
    role = models.CharField(max_length=10, choices=Role.choices)
    is_active = models.BooleanField(default=True)  
    is_staff = models.BooleanField(default=False)
    
     # Faculty-specific fields
    department = models.CharField(max_length=100, choices=[
        ('CSE', 'CSE'),
        ('EEE', 'EEE'),
        ('BBA', 'BBA'),
        ('English', 'English'),
        ('LLB', 'LLB'),
        ('Architecture', 'Architecture')
    ], blank=True, null=True)
    designation = models.CharField(max_length=100, blank=True, null=True)
    student_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    mobile_number = models.CharField(max_length=20, blank=True, null=True)
    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT 
    )

    date_joined = models.DateTimeField(auto_now_add=True)
    
    objects =  UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.first_name + ' ' + self.last_name

   
        
            

        
      