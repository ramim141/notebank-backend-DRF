from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings 
from .models import Note, Rating, Like, Bookmark
from taggit.serializers import (TagListSerializerField, TaggitSerializer)
from notifications.models import Notification

User = get_user_model()

class RatingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_student_id = serializers.CharField(source='user.student_id', read_only=True, allow_null=True) 

    class Meta:
        model = Rating
        fields = (
            'id', 
            'user', 
            'user_username', 
            'user_student_id', 
            'stars', 
            'comment', 
            'created_at', 
            'updated_at', 
            'note'
        )
        read_only_fields = ('user_username', 'user_student_id', 'created_at', 'updated_at')
        extra_kwargs = {
            'user': {'write_only': True, 'required': False}, 
            'note': {'write_only': True, 'required': True}  
        }




class NoteSerializer(serializers.ModelSerializer):
    uploader_username = serializers.CharField(source='uploader.username', read_only=True)
    uploader_student_id = serializers.CharField(source='uploader.student_id', read_only=True, allow_null=True) 
    uploader_department = serializers.CharField(source='uploader.department', read_only=True, allow_null=True) 

    file_url = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    note_ratings = RatingSerializer(many=True, read_only=True) 
    average_rating = serializers.FloatField(read_only=True) 
    likes_count = serializers.SerializerMethodField()
    is_liked_by_current_user = serializers.SerializerMethodField()
    bookmarks_count = serializers.SerializerMethodField() 
    is_bookmarked_by_current_user = serializers.SerializerMethodField()

    class Meta:
        model = Note
        fields = (
            'id', 
            'uploader', 
            'uploader_username', 
            'uploader_student_id',
            'uploader_department',
            'title', 
            'description', 
            'file_url', 
            'file',     
            'course_name', 
            'department_name', 
            'semester', 
            'tags',
            
            'download_count', 
            'average_rating', 
            'likes_count',
            'is_liked_by_current_user', 
            'bookmarks_count',
            'is_bookmarked_by_current_user',
            'note_ratings',
            'created_at', 
            'updated_at',
            
            
        )
        read_only_fields = (
            'uploader_username', 
            'uploader_student_id',
            'uploader_department',
            'download_count', 
            # 'average_rating', 
            'note_ratings',
            'created_at', 
            'updated_at', 
            'file_url',
            'likes_count', 
            'is_liked_by_current_user' 
            'bookmarks_count',
            'is_bookmarked_by_current_user'
        )
        extra_kwargs = {
            'file': {'write_only': True, 'required': True}, 
            'uploader': {'write_only': True, 'required': False}
        }
        
    def get_file_url(self, obj):
        request = self.context.get('request')
        if obj.file and hasattr(obj.file, 'url'):
            if request: 
                return request.build_absolute_uri(obj.file.url)
            return obj.file.url 
        return None
    
    def get_likes_count(self, obj):
        return obj.likes.count() 

    def get_is_liked_by_current_user(self, obj):
      
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return Like.objects.filter(note=obj, user=user).exists()
        return False 
    def get_bookmarks_count(self, obj):
        return obj.bookmarks.count() 

    def get_is_bookmarked_by_current_user(self, obj):
        user = self.context.get('request').user
        if user and user.is_authenticated:
            return Bookmark.objects.filter(note=obj, user=user).exists()
        return False


    
    def create(self, validated_data):
        note = Note.objects.create(**validated_data)
        return note

    def update(self, instance, validated_data):
        new_file = validated_data.get('file')
        if new_file and instance.file: 
            instance.file.delete(save=False) 
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        instance.save()
        return instance


class LikeSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True) 
    note_title = serializers.CharField(source='note.title', read_only=True) 

    class Meta:
        model = Like
        fields = ('id', 'user', 'user_username', 'note', 'note_title', 'created_at')
        read_only_fields = ('user', 'user_username', 'note_title', 'created_at')
        extra_kwargs = {
            'note': {'write_only': True, 'required': True} 
        }

    def create(self, validated_data):    
        return super().create(validated_data)



class BookmarkSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    note_title = serializers.CharField(source='note.title', read_only=True)

    class Meta:
        model = Bookmark
        fields = ('id', 'user', 'user_username', 'note', 'note_title', 'created_at')
        read_only_fields = ('user', 'user_username', 'note_title', 'created_at')
        extra_kwargs = {
            'note': {'write_only': True, 'required': True} 
        }
    
    
    def create(self, validated_data):
        return super().create(validated_data)



class NotificationSerializer(serializers.ModelSerializer):
    actor = serializers.StringRelatedField(read_only=True, allow_null=True) 
    target = serializers.StringRelatedField(read_only=True, allow_null=True)
    action_object = serializers.StringRelatedField(read_only=True, allow_null=True)
    

    class Meta:
        model = Notification
        fields = (
            'id', 
            'level',        
            'recipient',    
            'unread',       
            'timestamp',    
            'verb',         
            'description', 
            'actor',        
            'target',       
            'action_object',
           
        )

        read_only_fields = fields 


 