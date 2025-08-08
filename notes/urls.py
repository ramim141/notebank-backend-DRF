# notes/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ( 
                    NoteViewSet, 
                    StarRatingViewSet, 
                    CommentViewSet, 
                    DepartmentViewSet, 
                    CourseViewSet, 
                    NoteCategoryViewSet,
                    MyNoteRequestsView, 
                    FacultyViewSet, 
                    ContributorViewSet,
                    PublicNoteRequestViewSet,
                    test_note_request_create
                )


router = DefaultRouter()
router.register(r'public-note-requests', PublicNoteRequestViewSet, basename='public-note-request')
router.register(r'contributors', ContributorViewSet, basename='contributor')
router.register(r'faculties', FacultyViewSet, basename='faculty')
router.register(r'categories', NoteCategoryViewSet, basename='note-category')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'courses', CourseViewSet, basename='course') 
router.register(r'star-ratings', StarRatingViewSet, basename='star-rating')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'notes', NoteViewSet, basename='note')

urlpatterns = [
    # Place specific paths before router to avoid conflicts
    # Use a more specific path to avoid router conflicts
    path('requests/my-note-requests/', MyNoteRequestsView.as_view(), name='my-note-request-list-create'),
    path('requests/test-note-request/', test_note_request_create, name='test-note-request-create'),
    # Legacy paths to support existing frontend calls
    path('my-note-requests/', MyNoteRequestsView.as_view(), name='my-note-request-list-create-legacy'),
    path('notes/my-note-requests/', MyNoteRequestsView.as_view(), name='my-note-request-list-create-notes-prefix'),
    path('', include(router.urls)), 
    

    # path('download/<int:pk>/', download_note_file, name='secure-note-download'),
]