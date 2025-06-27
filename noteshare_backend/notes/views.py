# notes/views.py

from rest_framework import viewsets, permissions, status, serializers, generics
import rest_framework
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter

from .models import Note, StarRating, Comment, Like, Bookmark, Department, Course, NoteCategory, NoteRequest, Faculty, Contributor
from .serializers import NoteSerializer, StarRatingSerializer, CommentSerializer, LikeSerializer, BookmarkSerializer, DepartmentSerializer, CourseSerializer, NoteCategorySerializer, NoteRequestSerializer,  FacultySerializer, ContributorSerializer
from .permissions import IsOwnerOrReadOnly, IsRatingOrCommentOwnerOrReadOnly

from django.db.models import Avg, Count, Case, When, BooleanField, F, Value 
from django.db.models.functions import Coalesce
from rest_framework.exceptions import PermissionDenied
import logging
from .filters import ContributorFilter
logger = logging.getLogger(__name__)
from django.db import IntegrityError

class FacultyViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Faculty.objects.all().order_by('name')
    serializer_class = FacultySerializer
    permission_classes = [permissions.AllowAny]


class NoteCategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = NoteCategory.objects.all().order_by('name')
    serializer_class = NoteCategorySerializer
    permission_classes = [permissions.AllowAny]


class NoteViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    serializer_class = NoteSerializer

    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = {
        'category__name': ['exact', 'icontains'],
        'department__name': ['exact', 'icontains'],
        'course__name': ['exact', 'icontains'],
        'semester': ['exact', 'icontains'],
        'uploader__username': ['exact'],
        'uploader__student_id': ['exact'],
        'tags__name': ['exact', 'in'],
        'is_approved': ['exact'],
    }
    search_fields = [
        'title',
        'tags__name',
        'description',
        'category__name',
        'course__name',
        'department__name',
        'faculty__name',
    ]
    ordering_fields = ['created_at', 'download_count', 'average_rating', 'title']

    def get_permissions(self):

        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny] 
        elif self.action in ['create', 'download', 'toggle_like', 'toggle_bookmark', 'my_uploaded_notes']:
            permission_classes = [permissions.IsAuthenticated]
        elif self.action == 'destroy':
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        else: # update, partial_update
            permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user
        queryset = Note.objects.all()

        queryset = queryset.select_related('uploader', 'department', 'course', 'category').prefetch_related(
            'star_ratings',
            'comments',
            'likes',
            'bookmarks'
        )

    
        base_annotations = {
            'calculated_average_rating': Coalesce(Avg('star_ratings__stars'), Value(0.0)),
            'calculated_likes_count': Count('likes', distinct=True),
            'calculated_bookmarks_count': Count('bookmarks', distinct=True),
        }

        if user.is_authenticated:
            
            user_specific_annotations = {
                'is_liked_by_current_user_annotated': Case(
                    When(likes__user=user, then=Value(True)), 
                    default=Value(False),
                    output_field=BooleanField()
                ),
                'is_bookmarked_by_current_user_annotated': Case(
                    When(bookmarks__user=user, then=Value(True)), 
                    default=Value(False),
                    output_field=BooleanField()
                )
            }
        else:
            
            user_specific_annotations = {
                'is_liked_by_current_user_annotated': Value(False, output_field=BooleanField()),
                'is_bookmarked_by_current_user_annotated': Value(False, output_field=BooleanField())
            }

        queryset = queryset.annotate(**base_annotations, **user_specific_annotations)


       
        if self.action in ['list', 'retrieve']:
            if not user.is_authenticated or not user.is_staff:
                queryset = queryset.filter(is_approved=True)

        return queryset.order_by('-created_at')


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
        response_data = serializer.data
        response_data = {
            "message": "Note submitted, wait for admin approval.", 
            "note": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)


    @action(detail=True, methods=['get'])
    def download(self, request, pk=None):
        note = self.get_object()
        note.download_count = F('download_count') + 1
        note.save(update_fields=['download_count'])
        note.refresh_from_db()

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
        try:
            note = self.get_object()
            user = request.user

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
            logger.error(f"Error toggling like for note {pk} by {user.username}: {e}", exc_info=True)
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=True, methods=['post'])
    def toggle_bookmark(self, request, pk=None):
        logger.info(f"Received POST request to toggle bookmark for note ID: {pk}")

        if not request.user.is_authenticated:
            logger.warning(f"Bookmark toggle request failed: User not authenticated.")
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = request.user
        logger.info(f"Authenticated user: {user.username} (ID: {user.id})")

        try:
            # নোটটি খুঁজে বের করার চেষ্টা করা হচ্ছে
            note = self.get_object() # Note.objects.get(pk=pk) যদি self.get_object() এটা করে থাকে
            logger.info(f"Successfully retrieved note: '{note.title}' (ID: {note.id})")
        except Note.DoesNotExist:
            logger.warning(f"Bookmark toggle request failed: Note with ID {pk} not found.")
            return Response(
                {"detail": "Note not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.error(f"Unexpected error fetching note {pk}: {e}", exc_info=True)
            return Response(
                {"detail": "An error occurred while fetching the note."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        try:
            # বুকমার্কের লজিক
            bookmark_instance = Bookmark.objects.filter(user=user, note=note).first()

            if bookmark_instance:
                logger.info(f"User {user.username} unbookmarking note {note.id}")
                bookmark_instance.delete()
                bookmarked = False
                message = "Note removed from bookmarks."
            else:
                logger.info(f"User {user.username} bookmarking note {note.id}")
                Bookmark.objects.create(user=user, note=note)
                bookmarked = True
                message = "Note bookmarked successfully."

            # বুকমার্ক কাউন্ট আপডেট
            bookmarks_count = note.bookmarks.count()
            logger.info(f"Bookmark toggle successful for note {note.id}. New count: {bookmarks_count}")

            return Response({
                "message": message,
                "bookmarked": bookmarked,
                "bookmarks_count": bookmarks_count
            }, status=status.HTTP_200_OK)

        except IntegrityError as ie:
            # যদি একই ব্যবহারকারী একই নোট দুবার বুকমার্ক করার চেষ্টা করে (unique constraint violation)
            logger.error(f"IntegrityError during bookmark toggle for note {pk} by {user.username}: {ie}", exc_info=True)
            return Response(
                {"detail": "You might have already bookmarked this note or there's a data integrity issue."},
                status=status.HTTP_400_BAD_REQUEST # Bad Request হতে পারে এখানে
            )
        except Exception as e:
            # অন্য কোনো সাধারণ এরর
            logger.error(f"Error toggling bookmark for note {pk} by {user.username}: {e}", exc_info=True)
            return Response(
                {"detail": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


    @action(detail=False, methods=['get'], url_path='my-notes')
    def my_uploaded_notes(self, request):
        """
        Returns a list of all notes uploaded by the currently authenticated user.
        """
        user = self.request.user

        queryset = Note.objects.filter(uploader=user).order_by('-created_at').select_related('uploader', 'department', 'course').prefetch_related(
            'star_ratings', 'comments', 'likes', 'bookmarks'
        )

        queryset = queryset.annotate(
            calculated_average_rating=Coalesce(Avg('star_ratings__stars'), Value(0.0)),
            calculated_likes_count=Count('likes', distinct=True),
            calculated_bookmarks_count=Count('bookmarks', distinct=True),
            is_liked_by_current_user_annotated=Case(
                When(likes__user=user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            ),
            is_bookmarked_by_current_user_annotated=Case(
                When(bookmarks__user=user, then=Value(True)),
                default=Value(False),
                output_field=BooleanField()
            )
        )


        queryset = self.filter_queryset(queryset)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    def perform_update(self, serializer):
        instance = self.get_object()
        user = self.request.user
        if user == instance.uploader and not user.is_staff:
            raise PermissionDenied("You are not allowed to edit this note. Only administrators can edit notes after creation, or if you want to update it, please delete it and upload a new one.")
        serializer.save()
        logger.info(f"Note '{instance.title}' (ID: {instance.id}) updated by user {user.username}.")




class DepartmentViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Department.objects.all().order_by('name')
    serializer_class = DepartmentSerializer
    permission_classes = [permissions.AllowAny] 

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Course.objects.all().order_by('name')
    serializer_class = CourseSerializer
    permission_classes = [permissions.AllowAny]
    filterset_fields = ['department'] 




class StarRatingViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    queryset = StarRating.objects.all()
    serializer_class = StarRatingSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRatingOrCommentOwnerOrReadOnly]

    def get_serializer_context(self,):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        note_id_from_request = self.request.data.get('note')
        if not note_id_from_request:
            raise serializers.ValidationError({"note": ["This field is required to create a rating."]})

        note_instance = get_object_or_404(Note, pk=note_id_from_request)

        existing_rating = StarRating.objects.filter(note=note_instance, user=self.request.user).first()
        if existing_rating:
            raise serializers.ValidationError({"detail": "You have already rated this note. You can update your existing rating by sending a PUT/PATCH request to its ID."})

        serializer.save(user=self.request.user, note=note_instance)

class CommentViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly, IsRatingOrCommentOwnerOrReadOnly]

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    def perform_create(self, serializer):
        note_id_from_request = self.request.data.get('note')
        if not note_id_from_request:
            raise serializers.ValidationError({"note": ["This field is required to create a comment."]})

        note_instance = get_object_or_404(Note, pk=note_id_from_request)

        existing_comment = Comment.objects.filter(note=note_instance, user=self.request.user).first()
        if existing_comment:
            raise serializers.ValidationError({"detail": "You have already commented on this note. You can update your existing comment by sending a PUT/PATCH request to its ID."})

        serializer.save(user=self.request.user, note=note_instance)


# class NotificationViewSet(viewsets.ReadOnlyModelViewSet):
#     serializer_class = NotificationSerializer
#     permission_classes = [permissions.IsAuthenticated]

#     def get_queryset(self):
#         """
#         This view should return a list of all the notifications
#         for the currently authenticated user.
#         """
#         return self.request.user.notifications.all().order_by('-timestamp')

#     @action(detail=False, methods=['get'], url_path='unread')
#     def unread_notifications(self, request):
#         """
#         Returns a list of unread notifications for the current user.
#         """
#         queryset = self.request.user.notifications.unread().order_by('-timestamp')
#         page = self.paginate_queryset(queryset)
#         if page is not None:
#             serializer = self.get_serializer(page, many=True)
#             return self.get_paginated_response(serializer.data)
#         serializer = self.get_serializer(queryset, many=True)
#         return Response(serializer.data)

#     @action(detail=False, methods=['post'], url_path='mark-all-as-read')
#     def mark_all_as_read(self, request):
#         self.request.user.notifications.mark_all_as_read()
#         return Response({"message": "All notifications marked as read."}, status=status.HTTP_200_OK)

#     @action(detail=True, methods=['post'], url_path='mark-as-read') # URL: /notifications/{pk}/mark-as-read/
#     def mark_as_read(self, request, pk=None):
#         notification = get_object_or_404(Notification, recipient=request.user, pk=pk)
#         notification.mark_as_read()
#         return Response({"message": "Notification marked as read."}, status=status.HTTP_200_OK)

#     @action(detail=True, methods=['post'], url_path='mark-as-unread') # URL: /notifications/{pk}/mark-as-unread/
#     def mark_as_unread(self, request, pk=None):
#         notification = get_object_or_404(Notification, recipient=request.user, pk=pk)
#         notification.mark_as_unread()
#         return Response({"message": "Notification marked as unread."}, status=status.HTTP_200_OK)

#     @action(detail=False, methods=['get'], url_path='unread-count')
#     def unread_count(self, request):
#         count = self.request.user.notifications.unread().count()
#         return Response({"unread_count": count}, status=status.HTTP_200_OK)



class NoteRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteRequestSerializer
    permission_classes = [permissions.IsAuthenticated] # শুধুমাত্র লগইন করা ব্যবহারকারীরাই অ্যাক্সেস পাবে

    def get_queryset(self):
        return NoteRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class ContributorViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Provides a read-only list of contributor profiles.
    The data comes from the pre-calculated Contributor model.
    """
    serializer_class = ContributorSerializer
    permission_classes = [permissions.AllowAny]

    queryset = Contributor.objects.select_related(
        'user', 'user__department'
    ).order_by('-note_contribution_count', '-average_star_rating')
    
    filter_backends = [DjangoFilterBackend, SearchFilter]
    # filterset_fields = ['user__department']
    filterset_class = ContributorFilter
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']
