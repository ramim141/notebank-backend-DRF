# notes/admin.py
from django.contrib import admin

from .models import Note, StarRating, Comment, Department, Course


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name', 'id') 
    search_fields = ('name',)

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'department', 'id')
    list_filter = ('department',)
    search_fields = ('name', 'department__name')




@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'uploader',
        'course',
        'department',
        'semester',
        'download_count',
        'average_rating',
        'is_approved',
        'created_at',
        'updated_at'
    )
    list_filter = ('department', 'course', 'semester', 'uploader', 'is_approved', 'created_at')
    search_fields = ('title', 'description', 'tags__name', 'uploader__username', 'course__name', 'department__name')
    readonly_fields = ('average_rating', 'download_count', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'uploader', 'description', 'file', 'is_approved')
        }),
        ('Categorization', {
            'fields': ('course', 'department', 'semester', 'tags') 
        }),
        ('Analytics (Read-Only)', {
            'fields': ('download_count', 'average_rating'),
            'classes': ('collapse',)
        }),
        ('Timestamps (Read-Only)', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(StarRating)
class StarRatingAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'user_username', 'stars', 'created_at')
    list_filter = ('stars', 'user', 'note__department__name', 'created_at')
    search_fields = ('note__title', 'user__username', 'note__department__name')
    readonly_fields = ('created_at', 'updated_at')

    def note_title(self, obj):
        return obj.note.title
    note_title.short_description = 'Note Title'
    note_title.admin_order_field = 'note__title'

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'User'
    user_username.admin_order_field = 'user__username'

# নতুন CommentAdmin
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'user_username', 'comment_summary', 'created_at')
    list_filter = ('user', 'note__department__name', 'created_at')
    search_fields = ('note__title', 'user__username', 'text', 'note__department__name')
    readonly_fields = ('created_at', 'updated_at')

    def note_title(self, obj):
        return obj.note.title
    note_title.short_description = 'Note Title'
    note_title.admin_order_field = 'note__title'

    def user_username(self, obj):
        return obj.user.username
    user_username.short_description = 'User'
    user_username.admin_order_field = 'user__username'

    def comment_summary(self, obj):
        if obj.text:
            return (obj.text[:50] + '...') if len(obj.text) > 50 else obj.text
        return "-"
    comment_summary.short_description = 'Comment'