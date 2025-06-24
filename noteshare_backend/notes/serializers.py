# notes/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.conf import settings
from .models import Note, StarRating, Comment, Like, Bookmark , Department, Course, NoteCategory, NoteRequest,Faculty,Contributor
from taggit.serializers import (TagListSerializerField, TaggitSerializer)


User = get_user_model()


class ContributorSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    batch = serializers.CharField(source='user.batch', read_only=True)
    section = serializers.CharField(source='user.section', read_only=True)
    
    department_name = serializers.CharField(source='user.department', read_only=True, allow_null=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    
    class Meta:
        model = Contributor
        fields = [
            'full_name',
            'batch',
            'section',
            'department_name',
            'email',
            'note_contribution_count',
            'average_star_rating',
            'updated_at',
        ]


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = ['id', 'name', 'department', 'email']

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

# notes/serializers.py

class DepartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Department
        fields = ['id', 'name']

class CourseSerializer(serializers.ModelSerializer):
    department_name = serializers.CharField(source='department.name', read_only=True)
    class Meta:
        model = Course
        fields = ['id', 'name', 'department', 'department_name']
        # extra_kwargs = {                 # ❌ এই ব্লকটি সম্পূর্ণভাবে সরিয়ে দিন
        #     'department': {'write_only': True}
        # }
        # অথবা শুধু 'write_only' ট্রু কে False বা সরিয়ে দিন:
        # extra_kwargs = {
        #     'department': {'write_only': False} # অথবা এই লাইনটিই সরিয়ে দিন
        # }


class NoteCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = NoteCategory
        fields = ['id', 'name', 'description']



# StarRatingSerializer
class StarRatingSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True)
    user_student_id = serializers.CharField(source='user.student_id', read_only=True, allow_null=True)

    class Meta:
        model = StarRating 
        fields = (
            'id',
            'user',
            'user_username',
            'user_first_name',
            'user_last_name',
            'user_student_id',
            'stars',
            'created_at',
            'updated_at',
            'note'
        )
        read_only_fields = ('user_username', 'user_first_name', 'user_last_name', 'user_student_id', 'created_at', 'updated_at')
        extra_kwargs = {
            'user': {'write_only': True, 'required': False},
            'note': {'write_only': True, 'required': True}
        }


class CommentSerializer(serializers.ModelSerializer):
    user_username = serializers.CharField(source='user.username', read_only=True)
    user_student_id = serializers.CharField(source='user.student_id', read_only=True, allow_null=True)
    user_first_name = serializers.CharField(source='user.first_name', read_only=True, allow_null=True)
    user_last_name = serializers.CharField(source='user.last_name', read_only=True, allow_null=True)
    class Meta:
        model = Comment 
        fields = (
            'id',
            'user',
            'user_username',
            'user_first_name',
            'user_last_name',
            'user_student_id',
            'text', 
            'created_at',
            'updated_at',
            'note'
        )
        read_only_fields = ('user_username', 'user_first_name', 'user_last_name', 'user_student_id', 'created_at', 'updated_at')
        extra_kwargs = {
            'user': {'write_only': True, 'required': False},
            'note': {'write_only': True, 'required': True}
        }


class NoteSerializer(serializers.ModelSerializer):
    uploader_username = serializers.CharField(source='uploader.username', read_only=True)
    uploader_student_id = serializers.CharField(source='uploader.student_id', read_only=True, allow_null=True)
    uploader_department = serializers.CharField(source='uploader.department', read_only=True, allow_null=True)
    uploader_first_name = serializers.CharField(source='uploader.first_name', read_only=True, allow_null=True)
    uploader_last_name = serializers.CharField(source='uploader.last_name', read_only=True, allow_null=True)
    file_url = serializers.SerializerMethodField()
    tags = TagListSerializerField(required=False)
    department = serializers.PrimaryKeyRelatedField(queryset=Department.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)
    category_name = serializers.CharField(source='category.name', read_only=True, allow_null=True)
    category = serializers.PrimaryKeyRelatedField(queryset=NoteCategory.objects.all(), required=False, allow_null=True)
    faculty = serializers.PrimaryKeyRelatedField(queryset=Faculty.objects.all(), required=False, allow_null=True)
    department_name = serializers.CharField(source='department.name', read_only=True)
    course_name = serializers.CharField(source='course.name', read_only=True)
    faculty_name = serializers.CharField(source='faculty.name', read_only=True, allow_null=True)
    
    star_ratings = StarRatingSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    
    average_rating = serializers.FloatField(source='calculated_average_rating', read_only=True)
    likes_count = serializers.IntegerField(source='calculated_likes_count', read_only=True)
    is_liked_by_current_user = serializers.BooleanField(source='is_liked_by_current_user_annotated', read_only=True)
    bookmarks_count = serializers.IntegerField(source='calculated_bookmarks_count', read_only=True)
    is_bookmarked_by_current_user = serializers.BooleanField(source='is_bookmarked_by_current_user_annotated', read_only=True)

    class Meta:
        model = Note
        fields = (
            'id',
            'uploader',
            'uploader_username',
            'uploader_first_name',
            'uploader_last_name',
            'uploader_student_id',
            'uploader_department',
            'title',
            'description',
            'file_url',
            'file',
            'faculty',     
            'faculty_name', 
            'course',
            'category',
            'category_name',
            'department',
            'course_name',
            'department_name',
            'semester',
            'tags',
            'is_approved',
            'download_count',
            'average_rating',
            'likes_count',
            'is_liked_by_current_user',
            'bookmarks_count',
            'is_bookmarked_by_current_user',
            'star_ratings', 
            'comments',    
            'created_at',
            'updated_at',
        )
        read_only_fields = (
            'uploader_username',
            'uploader_student_id',
            'uploader_department',
            'download_count',
            'star_ratings', 
            'comments',     
            'updated_at',
            'file_url',
            'likes_count',
            'is_liked_by_current_user',
            'bookmarks_count',
            'is_bookmarked_by_current_user' ,
            'is_approved',
            'department_name',
            'category_name',
            'course_name',
            'faculty_name',
        )
        extra_kwargs = {
            'file': {'write_only': True, 'required': True},
            'uploader': {'write_only': True, 'required': False},
            'category': {'required': True, 'allow_null': False},
            'course': {'required': False, 'allow_null': True}, 
            'department': {'required': False, 'allow_null': True},
            'faculty': {'required': False, 'allow_null': True}
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


# class NotificationSerializer(serializers.ModelSerializer):
#     actor = serializers.StringRelatedField(read_only=True, allow_null=True)
#     target = serializers.StringRelatedField(read_only=True, allow_null=True)
#     action_object = serializers.StringRelatedField(read_only=True, allow_null=True)


#     class Meta:
#         model = Notification
#         fields = (
#             'id',
#             'level',
#             'recipient',
#             'unread',
#             'timestamp',
#             'verb',
#             'description',
#             'actor',
#             'target',
#             'action_object',
#         )
#         read_only_fields = fields


class NoteRequestSerializer(serializers.ModelSerializer):

    user_username = serializers.CharField(source='user.username', read_only=True)
    user_full_name = serializers.CharField(source='user.get_full_name', read_only=True)
    user_student_id = serializers.CharField(source='user.student_id', read_only=True)

    class Meta:
        model = NoteRequest
        fields = [
            'id', 
            'user',             
            'user_username',     
            'user_full_name',    
            'user_student_id',   
            'course_name', 
            'department_name', 
            'message', 
            'status', 
            'created_at'
        ]
    
        read_only_fields = ['user', 'status', 'created_at']