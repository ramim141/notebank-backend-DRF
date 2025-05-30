# notes/permissions.py
from rest_framework import permissions

class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object (note) to edit or delete it.
    Allows read-only access for any request (GET, HEAD, OPTIONS).
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.uploader == request.user

# StarRating এবং Comment উভয়ের জন্য এই Permission ব্যবহার করা যেতে পারে
class IsRatingOrCommentOwnerOrReadOnly(permissions.BasePermission): # নাম পরিবর্তন
    """
    Custom permission to only allow owners of a rating/comment to edit or delete it.
    Allows read-only access for any request.
    """
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.user == request.user