# notes/serializers.py

from rest_framework import serializers
from .models import Note, Category, NoteRating, NoteComment


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'


class NoteSerializer(serializers.ModelSerializer):
    
    uploaded_by = serializers.ReadOnlyField(source='uploaded_by.email')
    user = serializers.StringRelatedField(read_only=True)
    download_count = serializers.IntegerField(read_only=True)
    

    class Meta:
        model = Note
        fields = '__all__'
        read_only_fields = ['uploaded_by', 'download_count', 'created_at']


class NoteRatingSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = NoteRating
        fields = ['id', 'title', 'description', 'file', 'uploaded_by', 'course_name', 'category', 'download_count']
        read_only_fields = ['uploaded_by', 'download_count']

class NoteCommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = NoteComment
        fields = '__all__'
