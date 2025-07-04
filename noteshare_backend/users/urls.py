from django.urls import path, include
from rest_framework_simplejwt.views import (
    TokenObtainPairView, 
    TokenRefreshView,
    TokenVerifyView, 
    TokenBlacklistView,
)
from .views import (
    UserRegistrationView, CustomTokenObtainPairView, UserProfileView, ChangePasswordView , EmailVerificationView, PasswordResetRequestView, PasswordResetConfirmView
    , UserLinkedNotesViewSet, SiteStatsView , DashboardDataView 
)

from rest_framework.routers import DefaultRouter
router = DefaultRouter()
router.register(r'user-activity', UserLinkedNotesViewSet, basename='user-activity')

urlpatterns = [

    path('register/', UserRegistrationView.as_view(), name='user_register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'), 
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),

    path('logout/', TokenBlacklistView.as_view(), name='token_blacklist'),


    path('profile/', UserProfileView.as_view(), name='user_profile'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('verify-email/<uuid:token>/', EmailVerificationView.as_view(), name='user_email_verify'),

    path('password-reset/', PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset-confirm/<str:uidb64>/<str:token>/', PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('', include(router.urls)),
    path('site-stats/', SiteStatsView.as_view(), name='site-stats'),
    path('dashboard/', DashboardDataView.as_view(), name='dashboard-data'),
    
]