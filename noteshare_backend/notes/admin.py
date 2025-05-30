# notes/admin.py
from django.contrib import admin
# নতুন মডেলগুলি ইম্পোর্ট করুন
from .models import Note, StarRating, Comment

@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'uploader',
        'course_name',
        'department_name',
        'semester',
        'download_count',
        'average_rating',
        'created_at',
        'updated_at'
    )
    list_filter = ('department_name', 'course_name', 'semester', 'uploader', 'created_at')
    search_fields = ('title', 'description', 'tags__name', 'uploader__username', 'course_name', 'department_name') # tags কে tags__name করা হয়েছে
    readonly_fields = ('average_rating', 'download_count', 'created_at', 'updated_at')

    fieldsets = (
        (None, {
            'fields': ('title', 'uploader', 'description', 'file')
        }),
        ('Categorization', {
            'fields': ('course_name', 'department_name', 'semester', 'tags')
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

# নতুন StarRatingAdmin
@admin.register(StarRating)
class StarRatingAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'user_username', 'stars', 'created_at')
    list_filter = ('stars', 'user', 'note__department_name', 'created_at')
    search_fields = ('note__title', 'user__username')
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
    list_filter = ('user', 'note__department_name', 'created_at')
    search_fields = ('note__title', 'user__username', 'text')
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