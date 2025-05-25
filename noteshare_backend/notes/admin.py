from django.contrib import admin
from .models import Note, Rating

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
    search_fields = ('title', 'description', 'tags', 'uploader__username', 'course_name', 'department_name')
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

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     if db_field.name == "uploader":
    #         kwargs["initial"] = request.user.id
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)


    # def get_readonly_fields(self, request, obj=None):
    #     if obj: 
    #         return self.readonly_fields + ('uploader',)
    #     return self.readonly_fields


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    list_display = ('note_title', 'user_username', 'stars', 'comment_summary', 'created_at')
    list_filter = ('stars', 'user', 'note__department_name', 'created_at') 
    search_fields = ('note__title', 'user__username', 'comment')
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
        if obj.comment:
            return (obj.comment[:50] + '...') if len(obj.comment) > 50 else obj.comment
        return "-"
    comment_summary.short_description = 'Comment'