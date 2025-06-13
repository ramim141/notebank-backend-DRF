# notes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, StarRatingViewSet, CommentViewSet, NotificationViewSet, DepartmentViewSet, CourseViewSet


router = DefaultRouter()

router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'courses', CourseViewSet, basename='course') 
router.register(r'star-ratings', StarRatingViewSet, basename='star-rating')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'', NoteViewSet, basename='note') 
router.register(r'notifications', NotificationViewSet, basename='notification')
urlpatterns = [
    path('', include(router.urls)), 
    # path('my-notes/', MyNotesView.as_view(), name='my_notes'),
]