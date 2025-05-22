from rest_framework import serializers
from .models  import User
from django.contrib.auth.password_validation import validate_password


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    
    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'password', 'role',
            'department', 'designation', 'mobile_number', 'student_id'
        )

    def validate(self, data):
        role = data.get('role')

        if role == User.Role.FACULTY:
            missing_fields = []
            for field in ['department', 'designation', 'mobile_number']:
                if not data.get(field):
                    missing_fields.append(field)
            if missing_fields:
                raise serializers.ValidationError({field: f"{field} is required for faculty." for field in missing_fields})
            # Clear student-only fields
            data['student_id'] = None

        elif role == User.Role.STUDENT:
            if not data.get('student_id'):
                raise serializers.ValidationError({'student_id': 'student_id is required for student.'})
            # Clear faculty-only fields
            data['designation'] = None

        return data

            
    
    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserSerializer(serializers.ModelSerializer):
    student_id = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'role',
            'department', 'designation', 'mobile_number', 'student_id'
        )
    
    def get_student_id(self, obj):
        if obj.role == User.Role.STUDENT:
            return obj.id  
        return None
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        role = instance.role

        if role == User.Role.STUDENT:
            allowed_fields = ['student_id', 'email', 'first_name', 'last_name', 'mobile_number', 'department']
        elif role == User.Role.FACULTY:
            allowed_fields = ['first_name', 'last_name', 'email', 'designation', 'mobile_number', 'department']
        else:
            allowed_fields = []

        return {field: rep.get(field) for field in allowed_fields}


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()
    

class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField(write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords do not match.")
        return data