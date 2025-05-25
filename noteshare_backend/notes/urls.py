# notes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, RatingViewSet, NotificationViewSet


router = DefaultRouter()


router.register(r'ratings', RatingViewSet, basename='rating') 
router.register(r'', NoteViewSet, basename='note') 
router.register(r'notifications', NotificationViewSet, basename='notification')
urlpatterns = [
    path('', include(router.urls)), 
]