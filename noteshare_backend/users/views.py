from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView # লগইনের জন্য
from rest_framework.decorators import action

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
from notes.models import Note 
from rest_framework import viewsets, permissions

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
    """
    কাস্টম লগইন ভিউ (যদি লগইন রেসপন্সে অতিরিক্ত কিছু পাঠাতে চান)।
    আপাতত ডিফল্ট ব্যবহার করছি, তবে পরে কাস্টমাইজ করা যাবে।
    যেমন, টোকেনের সাথে ইউজারের কিছু তথ্যও পাঠানো যেতে পারে।

    যদি লগইন রেসপন্সে শুধু টোকেন চান, তাহলে সরাসরি TokenObtainPairView ব্যবহার করতে পারেন URL-এ।
    তবে কাস্টম ক্লাস রাখলে পরে পরিবর্তন করা সহজ হয়।
    """

    pass


class UserProfileView(generics.RetrieveUpdateAPIView):
  
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated] 

    def get_object(self):
        return self.request.user


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
    """
    ইমেইল ভেরিফিকেশন টোকেন ভ্যালিডেট করে এবং ইউজারকে ভেরিফাই করে।
    """
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

        password_reset_url = f"{frontend_url}/auth/reset-password/{uidb64}/{token}/"

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

    def post(self, request, uidb64, token, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        new_password = serializer.validated_data['new_password1']

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        token_generator = PasswordResetTokenGenerator()
        if user is not None and token_generator.check_token(user, token):
      
            user.set_password(new_password)
            user.save()
            return Response({"detail": "Password has been reset successfully."}, status=status.HTTP_200_OK)
        else:
            return Response({"detail": "The reset link was invalid or has expired. Please request a new one."}, status=status.HTTP_400_BAD_REQUEST)


class UserLinkedNotesViewSet(viewsets.ReadOnlyModelViewSet): 
  
    serializer_class = NoteSerializer 
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Note.objects.none() 

    @action(detail=False, methods=['get'], url_path='bookmarked-notes')
    def bookmarked_notes(self, request):
        user = request.user
        notes = Note.objects.filter(bookmarks__user=user).distinct().order_by('-bookmarks__created_at')
        page = self.paginate_queryset(notes)
        if page is not None:
            serializer = self.get_serializer(page, many=True) 
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='liked-notes')
    def liked_notes(self, request):
        user = request.user
        notes = Note.objects.filter(likes__user=user).distinct().order_by('-likes__created_at')

        page = self.paginate_queryset(notes)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
            
        serializer = self.get_serializer(notes, many=True)
        return Response(serializer.data)