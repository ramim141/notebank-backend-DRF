from rest_framework import generics, permissions, serializers
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import PasswordResetTokenGenerator

password_reset_token = PasswordResetTokenGenerator()
from .models import User
from django.core.mail import send_mail
from django.urls import reverse
from .serializers import RegisterSerializer, UserSerializer
from .utils import email_token_generator
from rest_framework.views import APIView
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse
from django.template.loader import render_to_string
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from rest_framework import status

from django.contrib.auth.tokens import default_token_generator
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import RetrieveUpdateAPIView


# Email Sending Utility
def send_verification_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_token_generator.make_token(user)
    verify_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    )

    subject = 'Verify Your Email - EduMetro'
    from_email = 'EduMetro <ahramu584@gmail.com>'
    to_email = [user.email]

    html_content = render_to_string('accounts/email.html', {
        'user': user,
        'verify_url': verify_url,
    })

    msg = EmailMultiAlternatives(subject, '', from_email, to_email)
    msg.attach_alternative(html_content, "text/html")
    msg.send()

# Registration View
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]
    
    def perform_create(self, serializer):
        user = serializer.save(is_active=False)
        send_verification_email(user, self.request)
        
# JWT Token View with User Info
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        user = User.objects.filter(email=attrs.get('email')).first()
        if user and not user.is_active:
            raise serializers.ValidationError("⚠️ Please verify your email before logging in.")
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# Email Verification View
class VerifyEmailView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, uidb64, token):
        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = get_object_or_404(User, pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return redirect("https://edumetro-ramim-ahmeds-projects.vercel.app/verify-error")  # invalid link

        if email_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect("https://edumetro-ramim-ahmeds-projects.vercel.app/login")  # successful verification
        else:
            return redirect("https://edumetro-ramim-ahmeds-projects.vercel.app/verify-error")  # expired or invalid token



# logout view
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Logged out successfully."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)




class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=400)
        user = User.objects.filter(email=email).first()
        if user:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = password_reset_token.make_token(user)
            reset_url = request.build_absolute_uri(
                reverse('password-reset-confirm', kwargs={'uidb64': uid, 'token': token})
            )
            # Send email (HTML and plain text both)
            subject = "Password Reset Requested - EduMetro"
            context = {
                "user": user,
                "reset_url": reset_url,
            }
            # Load HTML email template
            html_content = render_to_string("emails/password_reset_email.html", context)
            text_content = f"Hi {user.first_name},\n\nYou requested a password reset. Click the link below:\n{reset_url}\n\nIf you didn't request this, ignore this email.\nEduMetro Team"
            
            email_message = EmailMultiAlternatives(subject, text_content, settings.DEFAULT_FROM_EMAIL, [user.email])
            email_message.attach_alternative(html_content, "text/html")
            email_message.send()

        # We don't reveal if user exists or not for security
        return Response({"message": "If an account with this email exists, a password reset email has been sent."})


# Password Reset Confirm View


class PasswordResetConfirmView(APIView):
    def post(self, request):
        uidb64 = request.data.get('uid')
        token = request.data.get('token')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')

        if new_password != confirm_password:
            return Response({"error": "Passwords do not match."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = urlsafe_base64_decode(uidb64).decode()
            user = User.objects.get(pk=uid)
        except (User.DoesNotExist, ValueError, TypeError):
            return Response({"error": "Invalid UID."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Invalid or expired token."}, status=status.HTTP_400_BAD_REQUEST)

        user.set_password(new_password)
        user.save()

        return Response({"message": "Password has been reset successfully."}, status=status.HTTP_200_OK)


class ProfileView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user