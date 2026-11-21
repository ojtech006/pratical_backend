from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegisterView, LoginView, LogoutView, ForgotPasswordView,
    ResetPasswordView, ChangePasswordView, ProfileView,
)

urlpatterns = [
    path("register/", RegisterView.as_view(), name="account-register"),
    path("login/", LoginView.as_view(), name="account-login"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="account-logout"),
    path("password/forgot/", ForgotPasswordView.as_view(), name="password-forgot"),
    path("password/reset/", ResetPasswordView.as_view(), name="password-reset"),
    path("password/change/", ChangePasswordView.as_view(), name="password-change"),
    path("profile/", ProfileView.as_view(), name="account-profile"),
]
