from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserCreateAPIView.as_view(), name='user-register'),
    path('login/', LoginView.as_view(), name='user-login'),
    path('profile/<int:pk>/', ProfileView.as_view(), name='user-profile'),
    path('profile/delete/<int:pk>/', UserProfileDeleteAPIView.as_view(), name='user-delete'),
    path('profile/<int:user_id>/keywords/', KeywordDeleteView.as_view(), name='user-keyword-delete'),
    path('verify-email/', verify_email, name='verify-email'),
    path('send-verify-email/', send_verification_email,name='send-verification-email'),
]
