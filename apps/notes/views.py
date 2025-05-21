from rest_framework import viewsets, permissions
from .models import Note, Category, NoteRating, NoteComment
from .serializers import NoteSerializer, CategorySerializer, NoteRatingSerializer, NoteCommentSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.http import FileResponse, Http404
from django.core.exceptions import PermissionDenied
import os
from rest_framework.decorators import action

class NoteViewSet(viewsets.ModelViewSet):
    queryset = Note.objects.all().order_by('-upload_date')
    serializer_class = NoteSerializer
    # permission_classes = [permissions.IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['course_name', 'category']
    search_fields = ['title', 'course_name', 'description']

    def perform_create(self, serializer):
        serializer.save(uploaded_by=self.request.user)
    def perform_update(self, serializer):
        if self.request.user == serializer.instance.uploaded_by:
            serializer.save()
        else:
            raise PermissionDenied("You can only edit your own notes.")
    def perform_destroy(self, instance):
        if self.request.user == instance.uploaded_by:
            instance.delete()
        else:
            raise PermissionDenied("You can only delete your own notes.")
    
    # @action(detail=True, methods=['get'], url_path='download')
    # def download(self, request, pk=None):
    #     try:
    #         note = self.get_object()
    #         note.download_count += 1
    #         note.save()

    #         file_path = note.file.path
    #         if os.path.exists(file_path):
    #             return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    #         else:
    #             raise Http404("File not found")

    #     except Note.DoesNotExist:
    #         raise Http404("Note not found")


class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]


class NoteRatingViewSet(viewsets.ModelViewSet):
    queryset = NoteRating.objects.all()
    serializer_class = NoteRatingSerializer
    permission_classes = [permissions.IsAuthenticated]


class NoteCommentViewSet(viewsets.ModelViewSet):
    queryset = NoteComment.objects.all()
    serializer_class = NoteCommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class NoteDownloadViewSet(viewsets.ViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def download(self, request, pk=None):
        try:
            note = Note.objects.get(pk=pk)
            file_path = note.file.path
            if os.path.exists(file_path):
                return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
            else:
                raise Http404("File not found")
        except Note.DoesNotExist:
            raise Http404("Note not found")
