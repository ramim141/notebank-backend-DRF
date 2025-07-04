from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin 
from django.utils.html import format_html 

from .models import User 

@admin.register(User) 
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username', 
        'email', 
        'student_id', 
        'department', 
        'batch',
        'section',
        'first_name', 
        'last_name', 
        'bio',
        'is_staff', 
        'is_active', 
        'is_email_verified', 
        'profile_picture_thumbnail', 
        'date_joined',
        'last_login',
        'mobile_number',
        'university',
        'gender',
        'birthday',
        'get_skills_display', 
        'date_joined',
        'last_login',
    )
    

    list_display_links = ('username', 'email', 'student_id') 
    list_filter = BaseUserAdmin.list_filter + ('is_email_verified', 'is_active', 'is_staff', 'department', 'batch', 'section', 'gender', 'university', 'skills',) 
    search_fields = BaseUserAdmin.search_fields + ('email', 'student_id', 'department', 'mobile_number', 'university','skills__name',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': (
            'student_id',
            'department',
            'batch',
            'section',
            'university',
            'bio',
            'mobile_number',
            'website',
            'birthday',
            'gender',
            'skills' 
        )}),
        ('Email Verification', {'fields': ('is_email_verified', 'email_verification_token')}),
        ('Profile Information', {'fields': ('profile_picture', 'profile_picture_display')}),
    )
    
    readonly_fields = BaseUserAdmin.readonly_fields + (
        'email_verification_token',
        'profile_picture_display',
        'last_login',
        'date_joined',
        'get_skills_display', 
    )
    def profile_picture_thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />', obj.profile_picture.url)
        return "-" 
    profile_picture_thumbnail.short_description = 'Pic' 

    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="150" height="150" style="object-fit: cover;" />', obj.profile_picture.url)
        return "No image uploaded"
    profile_picture_display.short_description = 'Current Profile Picture'

    
    def get_skills_display(self, obj):
        return ", ".join([o.name for o in obj.skills.all()])
    get_skills_display.short_description = 'Skills'
 