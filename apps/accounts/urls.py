from django.urls import path
from .views import (
    RegisterView, CustomTokenObtainPairView, VerifyEmailView,
    PasswordResetRequestView, PasswordResetConfirmView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),

    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),

    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('verify-email/<uidb64>/<token>/', VerifyEmailView.as_view(), name='verify-email'),

    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),

    path('password-reset-confirm/', PasswordResetConfirmView.as_view(), name='password-reset-confirm'),
]
