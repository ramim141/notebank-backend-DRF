from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from taggit.managers import TaggableManager
import logging
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from notes.models import Department
logger = logging.getLogger(__name__)

User = get_user_model() 





class CustomTaggitSerializerField(serializers.Field):
    def to_representation(self, value):
        return list(value.names())

    def to_internal_value(self, data):
        if isinstance(data, str):
            data = [item.strip() for item in data.split(',') if item.strip()]

        if not isinstance(data, list):
            raise serializers.ValidationError("Expected a list of strings or a comma-separated string for tags.")
        if not all(isinstance(item, str) for item in data):
            raise serializers.ValidationError("All tag items must be strings.")
        return data


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        serializer = UserSerializer(self.user, context=self.context)
        data['user'] = serializer.data
        return data


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True, label="Confirm password")
    student_id = serializers.CharField(required=True) 
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)
    batch = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    section = serializers.CharField(required=False, allow_blank=True, allow_null=True)
    class Meta:
        model = User
        fields = (
            'username', 
            'email', 
            'password', 
            'password2', 
            'first_name', 
            'last_name', 
            'student_id', 
            'department', 
            'batch', 
            'section'
            )
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'email': {'required': True}, 
            'student_id': {'required': True}, 
            'department': {'required': False}, 
            'batch': {'required': False},
            'section': {'required': False},
            
        }

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with that email already exists.")
        return value

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs

    def create(self, validated_data):
        validated_data.pop('password2') 
        user = User.objects.create_user(**validated_data)
        return user
    def validate_student_id(self, value):
        if User.objects.filter(student_id=value).exists():
            raise serializers.ValidationError("A user with this Student ID already exists.")
        return value

class UserSerializer(serializers.ModelSerializer):
    profile_picture_url = serializers.SerializerMethodField(read_only=True)
    skills = CustomTaggitSerializerField(required=False)
    department_name = serializers.CharField(source='department.name', read_only=True, allow_null=True)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'first_name', 'last_name',
            'is_email_verified', 'student_id', 'department', 'department_name',
            'batch', 'section',
            'profile_picture_url', 
            'bio', 'mobile_number', 'university', 'website', 
            'birthday', 'gender', 'skills'
        )
        read_only_fields = (
            'username', 'id', 'is_email_verified', 'student_id', 'profile_picture_url', 'department_name'
        )
        extra_kwargs = {
            'first_name': {'required': False},
            'last_name': {'required': False},
            'department': {'required': False, 'allow_null': True, 'write_only': True},
            'batch': {'required': False, 'allow_blank': True, 'allow_null': True},
            'section': {'required': False, 'allow_blank': True, 'allow_null': True},
            'profile_picture': {'write_only': True, 'required': False},
            'bio': {'required': False, 'allow_blank': True, 'allow_null': True},
            'mobile_number': {'required': False, 'allow_blank': True, 'allow_null': True},
            'university': {'required': False, 'allow_blank': True, 'allow_null': True},
            'website': {'required': False, 'allow_blank': True, 'allow_null': True},
            'birthday': {'required': False, 'allow_null': True},
            'gender': {'required': False, 'allow_null': True},
        }
            
    def get_profile_picture_url(self, obj):
        if obj.profile_picture and hasattr(obj.profile_picture, 'url'):
          
            return obj.profile_picture.url
        return None
    
    def update(self, instance, validated_data):
        # Department আপডেট
        department = validated_data.pop('department', None)
        if department is not None:
            instance.department = department

        # Profile picture আপডেট
        profile_picture = validated_data.pop('profile_picture', None)
        if profile_picture is not None:
            if profile_picture == '':
                instance.profile_picture.delete()
            else:
                instance.profile_picture = profile_picture
        
        # Skills আপডেট
        skills_data = validated_data.pop('skills', None)
        if skills_data is not None:
            instance.skills.set(skills_data)
        
        # বাকি সব ফিল্ড আপডেট
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance
class ChangePasswordSerializer(serializers.Serializer):

    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True, validators=[validate_password]) 
    new_password2 = serializers.CharField(required=True, write_only=True, label="Confirm new password")

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Your old password was entered incorrectly. Please enter it again.")
        return value

    def validate(self, attrs):
        if attrs['new_password'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password": "The two new password fields didn't match."})

        if attrs['old_password'] == attrs['new_password']:
            raise serializers.ValidationError({"new_password": "New password cannot be the same as the old password."})
        return attrs

    def save(self, **kwargs):
        user = self.context['request'].user
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("No user is associated with this email address.")
        return value


class PasswordResetConfirmSerializer(serializers.Serializer):
 
    new_password1 = serializers.CharField(required=True, write_only=True, validators=[validate_password], label="New password")
    new_password2 = serializers.CharField(required=True, write_only=True, label="Confirm new password")
    

    def validate(self, attrs):
        if attrs['new_password1'] != attrs['new_password2']:
            raise serializers.ValidationError({"new_password2": "The two password fields didn't match."})
        return attrs


