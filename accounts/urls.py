from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import (
    CustomTokenObtainPairView,
    logout_view,
    profile_view,
    update_profile_view,
    change_password_view,
    user_sessions_view,
    terminate_session_view,
)


urlpatterns = [
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', logout_view, name='logout'),
    path('profile/', profile_view, name='profile'),
    path('profile/update/', update_profile_view, name='profile_update'),
    path('password/change/', change_password_view, name='change_password'),
    path('sessions/', user_sessions_view, name='user_sessions'),
    path('sessions/terminate/<int:session_id>/', terminate_session_view, name='terminate_session'),
]


