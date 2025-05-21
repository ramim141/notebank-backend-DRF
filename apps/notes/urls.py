# notes/urls.py
from rest_framework.routers import DefaultRouter
from .views import NoteViewSet, CategoryViewSet, NoteRatingViewSet, NoteCommentViewSet

router = DefaultRouter()
router.register(r'notes', NoteViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'ratings', NoteRatingViewSet)
router.register(r'comments', NoteCommentViewSet)

urlpatterns = router.urls

urlpatterns = router.urls


# http://127.0.0.1:8000/api/notes/<note_id>/download/