# notes/views.py
from rest_framework import viewsets, permissions, status, serializers 
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Note, Rating, Like, Bookmark 
from .serializers import NoteSerializer, RatingSerializer, NotificationSerializer 
from .permissions import IsOwnerOrReadOnly, IsRatingOwnerOrReadOnly
from notifications.models import Notification


class NoteViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    queryset = Note.objects.all().order_by('-created_at') 
    serializer_class = NoteSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        elif self.action in ['create', 'download', 'toggle_like', 'toggle_bookmark']: 
            permission_classes = [permissions.IsAuthenticated]
        else: 
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]
    
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = { 
        'department_name': ['exact', 'icontains'],
        'course_name': ['exact', 'icontains'],
        'semester': ['exact', 'icontains'],
        'uploader__username': ['exact'],
        'uploader__student_id': ['exact'],
        'tags__name': ['exact', 'in'], 
    }
    search_fields = [
        'title', 
        'tags__name', 
        'description', 
        'course_name', 
        'department_name'
    ]
    ordering_fields = ['created_at', 'download_count', 'average_rating', 'title']

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context


    def perform_create(self, serializer):
        serializer.save(uploader=self.request.user)


    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer) 
        headers = self.get_success_headers(serializer.data)
        response_data = {
            "message": "Note uploaded successfully!",
            "note": serializer.data 
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)
    
    @action(detail=True, methods=['get']) 
    def download(self, request, pk=None):
        note = self.get_object()
        note.download_count += 1
        note.save(update_fields=['download_count'])
        file_url = ""
        if note.file and hasattr(note.file, 'url'):
            file_url = request.build_absolute_uri(note.file.url)
        return Response({
            "detail": "Download initiated (count incremented). Please use the file_url to download.",
            "file_url": file_url,
            "download_count": note.download_count
        }, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'])  
    def toggle_like(self, request, pk=None):
        """
        Allows an authenticated user to like or unlike a note.
        If the user has already liked the note, it unlikes it. Otherwise, it likes it.
        """
        try:
            note = self.get_object()
            user = request.user

            if not user.is_authenticated:
                return Response(
                    {"detail": "Authentication required to like/unlike notes."},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            like_instance = Like.objects.filter(user=user, note=note).first()
            
            if like_instance:
       
                like_instance.delete()
                liked = False
                message = "Note unliked successfully."
            else:
    
                Like.objects.create(user=user, note=note)
                liked = True
                message = "Note liked successfully."
            
            likes_count = note.likes.count()

            return Response({
                "message": message,
                "liked": liked,
                "likes_count": likes_count
            }, status=status.HTTP_200_OK)

        except Note.DoesNotExist:
            return Response(
                {"detail": "Note not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    
    
    
    @action(detail=True, methods=['post'])
    def toggle_bookmark(self, request, pk=None):
      
        note = self.get_object()
        user = request.user

        try:
            bookmark_instance = Bookmark.objects.get(user=user, note=note)
            bookmark_instance.delete()
            bookmarked = False
            message = "Note removed from bookmarks."
        except Bookmark.DoesNotExist:
            Bookmark.objects.create(user=user, note=note)
            bookmarked = True
            message = "Note bookmarked successfully."
        
        bookmarks_count = note.bookmarks.count()

        return Response({
            "message": message,
            "bookmarked": bookmarked,
            "bookmarks_count": bookmarks_count
        }, status=status.HTTP_200_OK)





class RatingViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options', 'trace']
    queryset = Rating.objects.all()
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRatingOwnerOrReadOnly] 

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    
    def perform_create(self, serializer):
        note_id_from_request = self.request.data.get('note') 
        if not note_id_from_request:
            raise serializers.ValidationError({"note": ["This field is required to create a rating."]})

        note_instance = get_object_or_404(Note, pk=note_id_from_request)

        existing_rating = Rating.objects.filter(note=note_instance, user=self.request.user).first()
        if existing_rating:
            raise serializers.ValidationError({"detail": "You have already rated this note. You can update your existing rating."})

        serializer.save(user=self.request.user, note=note_instance)




class NotificationViewSet(viewsets.ReadOnlyModelViewSet): 
   
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_queryset(self):
        """
        This view should return a list of all the notifications
        for the currently authenticated user.
        """
        return self.request.user.notifications.all().order_by('-timestamp') 

    @action(detail=False, methods=['get'], url_path='unread')
    def unread_notifications(self, request):
        """
        Returns a list of unread notifications for the current user.
        """
        queryset = self.request.user.notifications.unread().order_by('-timestamp')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='mark-all-as-read')
    def mark_all_as_read(self, request):
        self.request.user.notifications.mark_all_as_read()
        return Response({"message": "All notifications marked as read."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-as-read') # URL: /notifications/{pk}/mark-as-read/
    def mark_as_read(self, request, pk=None):
        notification = get_object_or_404(Notification, recipient=request.user, pk=pk)
        notification.mark_as_read()
        return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='mark-as-unread') # URL: /notifications/{pk}/mark-as-unread/
    def mark_as_unread(self, request, pk=None):
        notification = get_object_or_404(Notification, recipient=request.user, pk=pk)
        notification.mark_as_unread()
        return Response({"message": "Notification marked as unread."}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get'], url_path='unread-count')
    def unread_count(self, request):
        count = self.request.user.notifications.unread().count()
        return Response({"unread_count": count}, status=status.HTTP_200_OK)

   