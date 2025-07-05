# notes/views.py

from rest_framework import viewsets, permissions, status, serializers, generics
import rest_framework
from rest_framework.response import Response
from rest_framework.decorators import action, api_view, permission_classes
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import FileResponse, Http404
import os
from django.views.decorators.cache import never_cache
from django.utils.decorators import method_decorator
import mimetypes
from rest_framework.reverse import reverse
from django.db.models import Exists, OuterRef
from rest_framework.pagination import PageNumberPagination
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

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10 
    page_size_query_param = 'page_size'
    max_page_size = 100
class NoteViewSet(viewsets.ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'patch', 'delete', 'head', 'options']
    serializer_class = NoteSerializer
    pagination_class = StandardResultsSetPagination
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
    ordering_fields = ['created_at', 'download_count', 'average_rating', 'title', 'likes_count', 'bookmarks_count']
    
    def get_permissions(self):
        # FIX: Added 'download' to IsAuthenticated permission check
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

        queryset = queryset.select_related('uploader', 'department', 'course', 'category', 'faculty').prefetch_related(
            'star_ratings',
            'comments',
        )

        # --- সমাধান: Annotation কী-গুলো Serializer-এর `source`-এর সাথে মেলানো হয়েছে ---
        base_annotations = {
            'calculated_average_rating': Coalesce(Avg('star_ratings__stars'), Value(0.0)),
            'calculated_likes_count': Count('likes', distinct=True),
            'calculated_bookmarks_count': Count('bookmarks', distinct=True),
        }
        queryset = queryset.annotate(**base_annotations)

        if user.is_authenticated:
            likes_subquery = Like.objects.filter(note=OuterRef('pk'), user=user)
            bookmarks_subquery = Bookmark.objects.filter(note=OuterRef('pk'), user=user)
            
            queryset = queryset.annotate(
                is_liked_by_current_user_annotated=Exists(likes_subquery),
                is_bookmarked_by_current_user_annotated=Exists(bookmarks_subquery)
            )
        else:
            queryset = queryset.annotate(
                is_liked_by_current_user_annotated=Value(False, output_field=BooleanField()),
                is_bookmarked_by_current_user_annotated=Value(False, output_field=BooleanField())
            )

        if self.action in ['list', 'retrieve']:
            if not user.is_authenticated or not user.is_staff:
                queryset = queryset.filter(is_approved=True)

        return queryset.order_by('-created_at', '-id')

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
            "message": "Note submitted, wait for admin approval.", 
            "note": serializer.data
        }
        return Response(response_data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=['get'], url_path='download')
    def download(self, request, pk=None):
        """
        Increments download count and serves the file for download.
        """
        try:
            note = self.get_object()
            
            # Increment download count atomically
            note.download_count = F('download_count') + 1
            note.save(update_fields=['download_count'])
            note.refresh_from_db() # Get the latest count from the DB

            if not note.file:
                logger.warning(f"Note {pk} has no file associated.")
                raise Http404("File not found for this note.")
            
            file_path = note.file.path
            if not os.path.exists(file_path):
                logger.error(f"File for note {pk} does not exist on disk at: {file_path}")
                raise Http404("File does not exist on the server.")
            
            file_name = os.path.basename(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
            if mime_type:
                response['Content-Type'] = mime_type
            
            # Add custom header with the new download count
            response['X-Download-Count'] = note.download_count
            return response
            
        except Http404 as e:
            return Response({"detail": str(e)}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Error serving file for note {pk}: {e}", exc_info=True)
            return Response({"detail": "An internal server error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- FIX: Updated Like Logic ---
    @action(detail=True, methods=['post'], url_path='toggle-like')
    def toggle_like(self, request, pk=None):
        note = self.get_object()
        user = request.user
        
        like_instance = Like.objects.filter(user=user, note=note)

        if like_instance.exists():
            like_instance.delete()
            liked = False
            message = "Note unliked successfully."
        else:
            Like.objects.create(user=user, note=note)
            liked = True
            message = "Note liked successfully."
        
        # --- সমাধান: এই লাইনটি যোগ করুন ---
        # ডেটাবেস থেকে নোটের সর্বশেষ অবস্থা লোড করুন
        note.refresh_from_db()
        
        # এখন কাউন্ট করলে সঠিক সংখ্যা পাওয়া যাবে
        likes_count = note.likes.count()

        return Response({
            "message": message,
            "liked": liked,
            "likes_count": likes_count
        }, status=status.HTTP_200_OK)


    # --- FIX: Updated Bookmark Logic ---
    @action(detail=True, methods=['post'], url_path='toggle-bookmark')
    def toggle_bookmark(self, request, pk=None):
        note = self.get_object()
        user = request.user

        bookmark_instance = Bookmark.objects.filter(user=user, note=note)

        if bookmark_instance.exists():
            bookmark_instance.delete()
            bookmarked = False
            message = "Note removed from bookmarks."
        else:
            Bookmark.objects.create(user=user, note=note)
            bookmarked = True
            message = "Note bookmarked successfully."

        # --- সমাধান: এই লাইনটি যোগ করুন ---
        note.refresh_from_db()

        bookmarks_count = note.bookmarks.count()

        return Response({
            "message": message,
            "bookmarked": bookmarked,
            "bookmarks_count": bookmarks_count
        }, status=status.HTTP_200_OK)

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


class NoteRequestListCreateView(generics.ListCreateAPIView):
    serializer_class = NoteRequestSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return NoteRequest.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)



class ContributorViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ContributorSerializer
    permission_classes = [permissions.AllowAny]

    queryset = Contributor.objects.select_related(
        'user', 'user__department'
    ).order_by('-note_contribution_count', '-average_star_rating')
    
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = ContributorFilter
    search_fields = ['user__username', 'user__first_name', 'user__last_name', 'user__email']

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def download_note_file(request, pk):
    try:
        note = Note.objects.get(pk=pk)
        
        note.download_count = F('download_count') + 1
        note.save(update_fields=['download_count'])
        note.refresh_from_db()

        if not note.file:
            logger.warning(f"Note {pk} has no file associated.")
            raise Http404("File not found.")
            
        file_path = note.file.path
        if not os.path.exists(file_path):
            logger.error(f"File for note {pk} does not exist on disk at: {file_path}")
            raise Http404("File not found.")
            
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)
        
        response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=file_name)
        if mime_type:
            response['Content-Type'] = mime_type
            
        return response
        
    except Note.DoesNotExist:
        logger.warning(f"Download request for non-existent note: {pk}")
        raise Http404("Note not found.")
    except Exception as e:
        logger.error(f"Error serving file for note {pk}: {e}", exc_info=True)
        raise Http404("An error occurred while trying to serve the file.")