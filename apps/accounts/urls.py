# users/urls.py
from django.urls import path
from .views import RegisterView, CustomTokenObtainPairView, VerifyEmailView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    # Register new user (Student or Faculty)
    path('register/', RegisterView.as_view(), name='register'),

    # Login using JWT Token
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    # Refresh JWT token
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Email verification link
    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),
]
