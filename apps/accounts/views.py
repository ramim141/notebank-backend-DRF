from rest_framework import generics, permissions
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from .models import User
from django.core.mail import send_mail
from django.urls import reverse
from .serializers import RegisterSerializer, UserSerializer
from .utils import email_token_generator
from rest_framework.views import APIView
from django.shortcuts import redirect, get_object_or_404
from django.utils.http import urlsafe_base64_decode
from django.http import HttpResponse


# Email Sending Utility
def send_verification_email(user, request):
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = email_token_generator.make_token(user)
    verify_url = request.build_absolute_uri(
        reverse('verify-email', kwargs={'uidb64': uid, 'token': token})
    )
    
    subject = 'Verify Your Email - EduMetro'
    message = (
        f"Hi {user.first_name} {user.last_name},\n\n"
        f"Thanks for registering on EduMetro.\n"
        f"Please verify your email by clicking the link below:\n\n"
        f"{verify_url}\n\n"
        f"If you didn't request this, please ignore this email.\n\n"
        f"Best regards,\nEduMetro Team"
    )
    
    send_mail(
        subject,
        message,
        'ahramu584@gmail.com',  
        [user.email],
        fail_silently=False,
    )

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
            return redirect("https://your-frontend-site.com/verify-error")  # invalid link

        if email_token_generator.check_token(user, token):
            user.is_active = True
            user.save()
            return redirect("https://your-frontend-site.com/login?verified=true")  # successful verification
        else:
            return redirect("https://your-frontend-site.com/verify-error")  # expired or invalid token



# logout view
class LogoutView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        try:
            request.user.auth_token.delete()
            return Response({"message": "Logged out successfully."}, status=200)
        except Exception as e:
            return Response({"error": str(e)}, status=400)


