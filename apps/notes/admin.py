from django.contrib import admin
from .models import Note, Category, NoteRating, NoteComment

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Note)
class NoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'course_name', 'category', 'upload_date', 'download_count', 'description')
    list_filter = ('course_name', 'category', 'upload_date')
    search_fields = ('title', 'course_name', 'user__first_name', 'user__email')
    


@admin.register(NoteRating)
class NoteRatingAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'user', 'rating')
    list_filter = ('rating',)
    search_fields = ('note__title', 'user__email')


@admin.register(NoteComment)
class NoteCommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'note', 'user', 'created_at')
    search_fields = ('note__title', 'user__email', 'comment')
    list_filter = ('created_at',)
    ordering = ('-created_at',)