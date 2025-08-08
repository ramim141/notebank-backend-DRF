from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView 
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from .serializers import UserRegistrationSerializer, UserSerializer, ChangePasswordSerializer, PasswordResetRequestSerializer, PasswordResetConfirmSerializer
from django.core.mail import send_mail
from django.template.loader import render_to_string 
from django.urls import reverse
from django.conf import settings 
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.contrib.auth.forms import SetPasswordForm
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.db import IntegrityError
from notes.serializers import NoteSerializer
from notes.models import Note, Course, Department
from rest_framework import viewsets, permissions
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.db.models import Case, When, Value, BooleanField
from django_filters.rest_framework import DjangoFilterBackend
from .filters import NoteFilter 
from .serializers import UserSerializer
from django.db.models import Count, Sum
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import CustomTokenObtainPairSerializer
from urllib.parse import unquote
User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True) #
        
        user = serializer.save() 

        email_sent_message = "User registered successfully. Please verify your email if required." 

        if user.email and user.email_verification_token:
            try:
                token = str(user.email_verification_token)
                relative_verification_url = reverse('user_email_verify', kwargs={'token': token})
                
                if hasattr(settings, 'BASE_API_URL') and settings.BASE_API_URL:
                    base_url = settings.BASE_API_URL
                else:  
                    base_url = f"{request.scheme}://{request.get_host()}" 
                
                full_verification_url = f"{base_url}{relative_verification_url}"

                email_subject = 'Verify your email address for NoteShare'
                
     
                plain_message = f"""
                Hi {user.username},

                Thank you for registering at NoteShare!
                Please click the link below to verify your email address:
                {full_verification_url}

                If you did not register for this account, please ignore this email.

                Thanks,
                The NoteShare Team
                """

        
                html_message = render_to_string('users/emails/verify_email.html', {
                    'user': user,
                    'verification_url': full_verification_url
                })
                
                email_obj = EmailMultiAlternatives( 
                    subject=email_subject,
                    body=plain_message, 
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email]
                )
                email_obj.attach_alternative(html_message, "text/html") 
                email_obj.send(fail_silently=False) 

                email_sent_message = "User registered successfully. A verification email has been sent."
            
            except Exception as e:
     
                print(f"ERROR sending verification email to {user.email} for user {user.username}: {e}")
       
                email_sent_message = "User registered successfully, but we encountered an issue sending the verification email. Please contact support or try to resend it later."
        
        elif not user.email:
            print(f"WARNING: User {user.username} registered without an email address. Cannot send verification email.")
       
        
        elif not user.email_verification_token: 
            print(f"WARNING: User {user.username} (email: {user.email}) does not have an email_verification_token. Cannot send verification email.")
  
 
        user_data = UserSerializer(user, context={'request': request}).data
        
        return Response({
            "user": user_data,
            "message": email_sent_message 
        }, status=status.HTTP_201_CREATED)




class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class UserProfileView(generics.RetrieveUpdateAPIView):
  
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_object(self):
        return self.request.user
    # def get_serializer_context(self):
    #     context = super().get_serializer_context()
    #     context['request'] = self.request
    #     return context


class ChangePasswordView(generics.UpdateAPIView):
   
    serializer_class = ChangePasswordSerializer
    model = User 
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, queryset=None):

        return self.request.user

    def update(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)

        if serializer.is_valid(raise_exception=True):

            serializer.save() 
            return Response({"detail": "Password updated successfully"}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class EmailVerificationView(generics.GenericAPIView): 
    permission_classes = [permissions.AllowAny] 

    def get(self, request, token, *args, **kwargs):
        try:
            user = get_object_or_404(User, email_verification_token=token)

            if user.is_email_verified:
                return Response({"detail": "Email already verified."}, status=status.HTTP_200_OK) 

            user.is_email_verified = True
            user.email_verification_token = None 
            user.save()

            return Response({"detail": "Email verified successfully."}, status=status.HTTP_200_OK)

        except User.DoesNotExist: 
            return Response({"detail": "Invalid or expired verification token."}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e: 
            print(f"Error during email verification: {e}")
            return Response({"detail": "An error occurred during email verification."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        


class PasswordResetRequestView(generics.GenericAPIView):
    
    serializer_class = PasswordResetRequestSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email_address = serializer.validated_data['email'] 
        
        try:
            user = User.objects.get(email=email_address)
        except User.DoesNotExist:
            return Response({"detail": "No user is associated with this email address."}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = token_generator.make_token(user)
        
        if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
            frontend_url = settings.FRONTEND_URL
        else:
            print("CRITICAL: FRONTEND_URL is not set in settings.py. Password reset emails will not have correct links.")
            return Response({"detail": "Server configuration error: Essential URL for password reset is missing."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        password_reset_url = f"{frontend_url}/reset-password/{uidb64}/{token}/"

        email_subject = 'Password Reset Request for NoteShare'

        plain_message = f"""
        Hi {user.username},

        You requested a password reset for your NoteShare account.
        Please use the following link to set a new password:
        {password_reset_url}

        If you did not request this, please ignore this email.
        This link is valid for a limited time.

        Thanks,
        The NoteShare Team
        """

        html_message = render_to_string('users/emails/password_reset_email.html', {
            'user': user,
            'password_reset_url': password_reset_url
        })
        
        try:
            email_message_obj = EmailMultiAlternatives(
                subject=email_subject,
                body=plain_message, 
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[user.email]
            )
            email_message_obj.attach_alternative(html_message, "text/html") 
            email_message_obj.send(fail_silently=False)
            
            return Response({"detail": "Password reset email has been sent. Please check your inbox."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            print(f"ERROR sending password reset email to {user.email}: {e}")
      
            return Response({"detail": "An error occurred while attempting to send the password reset email. Please try again later."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PasswordResetConfirmView(generics.GenericAPIView):
   
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token, *args, **kwargs):
        """Handle GET requests to validate the reset link before showing the form"""
        # Decode URL-encoded parameters
        decoded_uidb64 = unquote(uidb64)
        decoded_token = unquote(token)
        
        print(f"DEBUG: GET request for password reset with uidb64={decoded_uidb64}, token={decoded_token}")
        
        try:
            uid = force_str(urlsafe_base64_decode(decoded_uidb64))
            print(f"DEBUG: Decoded uid={uid}")
            user = User.objects.get(pk=uid)
            print(f"DEBUG: Found user={user.username}")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            print(f"DEBUG: Error decoding uidb64 or finding user: {e}")
            return Response({"detail": "Invalid reset link."}, status=status.HTTP_400_BAD_REQUEST)

        token_generator = PasswordResetTokenGenerator()
        token_valid = token_generator.check_token(user, decoded_token)
        print(f"DEBUG: Token valid={token_valid}")
        
        if token_valid:
            return Response({"detail": "Reset link is valid. Please proceed with password reset."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "The reset link was invalid or has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)

    def post(self, request, uidb64, token, *args, **kwargs):
        # Decode URL-encoded parameters
        decoded_uidb64 = unquote(uidb64)
        decoded_token = unquote(token)
        
        print(f"DEBUG: Password reset confirm called with uidb64={decoded_uidb64}, token={decoded_token}")
        
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_password = serializer.validated_data['new_password1']

        try:
            uid = force_str(urlsafe_base64_decode(decoded_uidb64))
            print(f"DEBUG: Decoded uid={uid}")
            user = User.objects.get(pk=uid)
            print(f"DEBUG: Found user={user.username}")
        except (TypeError, ValueError, OverflowError, User.DoesNotExist) as e:
            print(f"DEBUG: Error decoding uidb64 or finding user: {e}")
            user = None

        token_generator = PasswordResetTokenGenerator()
        token_valid = token_generator.check_token(user, decoded_token) if user else False
        print(f"DEBUG: Token valid={token_valid}")
        
        if user is not None and token_valid:
            print(f"DEBUG: Setting new password for user {user.username}")
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "The reset link was invalid or has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)


class UserLinkedNotesViewSet(viewsets.ReadOnlyModelViewSet): 
    serializer_class = NoteSerializer 
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.filter(is_approved=True).select_related(
            'uploader', 'department', 'course', 'category'
        ).prefetch_related('tags')

    def get_annotated_queryset(self, base_queryset):
        user = self.request.user
        return base_queryset.annotate(
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

    @action(detail=False, methods=['get'], url_path='bookmarked-notes')
    def bookmarked_notes(self, request):
        user = request.user
        base_queryset = self.get_queryset().filter(bookmarks__user=user)
        filtered_queryset = NoteFilter(request.query_params, queryset=base_queryset, request=request).qs
        annotated_queryset = self.get_annotated_queryset(filtered_queryset)
        final_queryset = annotated_queryset.order_by('-bookmarks__created_at')

        page = self.paginate_queryset(final_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True) 
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(final_queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='liked-notes')
    def liked_notes(self, request):
        
        user = request.user
        base_queryset = self.get_queryset().filter(likes__user=user)
        annotated_queryset = self.get_annotated_queryset(base_queryset)
        final_queryset = annotated_queryset.order_by('-likes__created_at')
        
        page = self.paginate_queryset(final_queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(final_queryset, many=True)
        return Response(serializer.data)

class SiteStatsView(APIView):
    permission_classes = [AllowAny]
    def get(self, request, *args, **kwargs):
        total_users = User.objects.count()
        total_notes = Note.objects.filter(is_approved=True).count() 
        total_courses = Course.objects.count()
        total_departments = Department.objects.count()


        stats_data = {
            "total_users": total_users,
            "total_notes": total_notes,
            "total_courses": total_courses,
            "total_departments": total_departments,
        }
        return Response(stats_data)


class BookmarkedNotesView(generics.ListAPIView):
    serializer_class = NoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    filter_backends = [DjangoFilterBackend]
    filterset_fields = {
        'category__name': ['exact'],
    }

    def get_queryset(self):
        user = self.request.user

        queryset = Note.objects.filter(
            bookmarks__user=user, 
            is_approved=True
        ).select_related(
            'uploader', 'department', 'course', 'category'
        ).prefetch_related(
            'tags', 'likes', 'bookmarks', 'star_ratings'
        )
        queryset = queryset.annotate(
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
        
        return queryset.order_by('-bookmarks__created_at')



class DashboardDataView(APIView):
    """
    Provides consolidated data for the user dashboard in a single API call.
    This view is optimized to reduce the number of database queries.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user

        user_serializer = UserSerializer(user, context={'request': request})
        user_data_with_stats = user_serializer.data

        stats_data = {
            'uploads': user_data_with_stats.get('total_notes_uploaded', 0),
            'downloads': user_data_with_stats.get('total_notes_downloaded', 0),
            'totalReviews': user_data_with_stats.get('total_reviews_received', 0),
            'avgRating': user_data_with_stats.get('average_rating_of_all_notes', 0.0),
        }

        recent_notes_qs = Note.objects.filter(
            uploader=user
        ).order_by('-created_at')[:5]
        recent_notes_data = NoteSerializer(recent_notes_qs, many=True, context={'request': request}).data

        bookmarked_notes_qs = Note.objects.filter(
            bookmarks__user=user,
            is_approved=True
        ).order_by('-bookmarks__created_at')[:5]
        recent_bookmarks_data = NoteSerializer(bookmarked_notes_qs, many=True, context={'request': request}).data
        category_distribution = Note.objects.filter(uploader=user) \
                                        .values('category__name') \
                                        .annotate(value=Count('id')) \
                                        .order_by('-value')
        
        pie_chart_colors = ["#6366F1", "#EC4899", "#F59E0B", "#10B981", "#8B5CF6", "#F43F5E"]
        
        pie_chart_data = [
            {**item, 'name': item['category__name'], 'color': pie_chart_colors[i % len(pie_chart_colors)]}
            for i, item in enumerate(category_distribution) if item.get('category__name')
        ]

        # চূড়ান্ত রেসপন্স ডেটা
        dashboard_data = {
            'user': user_data_with_stats,
            'stats': stats_data,
            'myNotes': recent_notes_data,
            'bookmarks': recent_bookmarks_data,
            'performanceData': pie_chart_data,
        }

        return Response(dashboard_data, status=status.HTTP_200_OK)