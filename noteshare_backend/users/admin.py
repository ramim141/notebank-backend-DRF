from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin # Django-র ডিফল্ট UserAdmin
from django.utils.html import format_html # অ্যাডমিনে HTML দেখানোর জন্য

from .models import User # আপনার কাস্টম User মডেল ইম্পোর্ট করুন

@admin.register(User) # admin.site.register(User, UserAdmin) এর শর্টকাট
class UserAdmin(BaseUserAdmin):
    # BaseUserAdmin থেকে আমরা অনেক কিছুই ইনহেরিট করবো (যেমন ইউজারনেম, পাসওয়ার্ড, গ্রুপ, পারমিশন ইত্যাদি দেখানোর ব্যবস্থা)
    
    # যে ফিল্ডগুলো লিস্ট ভিউতে (ইউজারদের তালিকা) দেখাতে চান
    list_display = (
        'username', 
        'email', 
        'student_id', 
        'department', 
        'first_name', 
        'last_name', 
        'is_staff', 
        'is_active', 
        'is_email_verified', # আমাদের নতুন ফিল্ড
        'profile_picture_thumbnail', # ছবির থাম্বনেইল দেখানোর জন্য (কাস্টম মেথড)
        'date_joined',
        'last_login',
    )
    
    # যে ফিল্ডগুলো লিস্ট ভিউতে লিঙ্ক হিসেবে কাজ করবে (ক্লিক করলে এডিট পেজে যাবে)
    list_display_links = ('username', 'email', 'student_id') # ইউজারনেম, ইমেইল ও স্টুডেন্ট আইডি লিঙ্ক হিসেবে থাকবে
    
    # যে ফিল্ডগুলো দিয়ে লিস্ট ভিউতে ফিল্টার করা যাবে
    list_filter = BaseUserAdmin.list_filter + ('is_email_verified', 'is_active', 'is_staff', 'department') # আমাদের নতুন ফিল্টারগুলো যোগ করা হলো
    
    # যে ফিল্ডগুলো দিয়ে সার্চ করা যাবে
    search_fields = BaseUserAdmin.search_fields + ('email', 'student_id', 'department') # email ও student_id দিয়েও সার্চ করার অপশন যোগ করা হলো

    # ইউজার এডিট পেজে ফিল্ডগুলো কীভাবে গ্রুপ করে দেখানো হবে
    # BaseUserAdmin-এর fieldsets ওভাররাইড করে নতুন ফিল্ড যোগ করা
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('student_id', 'department')}),
        ('Email Verification', {'fields': ('is_email_verified', 'email_verification_token')}),
        ('Profile Information', {'fields': ('profile_picture', 'profile_picture_display')}), # profile_picture_display কাস্টম মেথড
    )
    
    # যে ফিল্ডগুলো শুধু পড়া যাবে (এডিট করা যাবে না) ইউজার এডিট পেজে
    readonly_fields = BaseUserAdmin.readonly_fields + (
        'email_verification_token', # টোকেন শুধু দেখা যাবে, এডিট করা যাবে না
        'profile_picture_display',  # ছবির প্রিভিউ দেখানোর জন্য
        'last_login', 
        'date_joined',
    )

    # কাস্টম মেথড: লিস্ট ভিউতে প্রোফাইল ছবির থাম্বনেইল দেখানোর জন্য
    def profile_picture_thumbnail(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="40" height="40" style="object-fit: cover; border-radius: 50%;" />', obj.profile_picture.url)
        return "-" # যদি ছবি না থাকে
    profile_picture_thumbnail.short_description = 'Pic' # কলামের হেডার

    # কাস্টম মেথড: এডিট পেজে প্রোফাইল ছবির প্রিভিউ দেখানোর জন্য
    def profile_picture_display(self, obj):
        if obj.profile_picture:
            return format_html('<img src="{}" width="150" height="150" style="object-fit: cover;" />', obj.profile_picture.url)
        return "No image uploaded"
    profile_picture_display.short_description = 'Current Profile Picture'

    # যদি আপনি চান যে list_editable ব্যবহার করে লিস্ট ভিউ থেকেই কিছু ফিল্ড এডিট করা যাক
    # list_editable = ('is_active', 'is_staff', 'is_email_verified')
    # তবে list_editable ফিল্ডগুলো list_display_links এ থাকতে পারবে না।

# যদি আপনি Django-র ডিফল্ট Group মডেলও অ্যাডমিন প্যানেলে দেখতে চান (সাধারণত এটা থাকেই)
# from django.contrib.auth.models import Group
# admin.site.unregister(Group) # যদি কাস্টম GroupAdmin বানাতে চান, আগে আনরেজিস্টার করতে হতে পারে
# admin.site.register(Group)