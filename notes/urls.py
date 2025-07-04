# notes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
# download_note_file ইম্পোর্ট করার আর প্রয়োজন নেই
from .views import NoteViewSet, StarRatingViewSet, CommentViewSet, DepartmentViewSet, CourseViewSet, NoteCategoryViewSet, NoteRequestListCreateView, FacultyViewSet, ContributorViewSet


router = DefaultRouter()

router.register(r'contributors', ContributorViewSet, basename='contributor')
router.register(r'faculties', FacultyViewSet, basename='faculty')
router.register(r'categories', NoteCategoryViewSet, basename='note-category')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'courses', CourseViewSet, basename='course') 
router.register(r'star-ratings', StarRatingViewSet, basename='star-rating')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'', NoteViewSet, basename='note') 

urlpatterns = [
    path('note-requests/', NoteRequestListCreateView.as_view(), name='note-request-list-create'),
    path('', include(router.urls)), 
    

    # path('download/<int:pk>/', download_note_file, name='secure-note-download'),
]