"""
Authentication views using JWT tokens with custom logic.
"""
from datetime import datetime
from django.contrib.auth import authenticate
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from drf_spectacular.utils import extend_schema
import logging

from .models import User, UserSession
from .serializers import (
    CustomTokenObtainPairSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer
)
from core.utils import get_client_ip, get_user_agent

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom JWT token obtain view with additional security features.
    """
    serializer_class = CustomTokenObtainPairSerializer
    
    @extend_schema(
        summary="Obtain JWT token pair",
        description="Authenticate user and return access/refresh tokens with user info",
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
        except Exception as e:
            logger.warning(f"Failed login attempt from {get_client_ip(request)}: {str(e)}")
            return Response(
                {"error": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        user = serializer.user
        ip_address = get_client_ip(request)
        user_agent = get_user_agent(request)
        
        # Update user login info
        user.last_login_ip = ip_address
        user.failed_login_attempts = 0
        user.is_active_session = True
        user.save(update_fields=['last_login_ip', 'failed_login_attempts', 'is_active_session'])
        
        # Create session record
        session_key = request.session.session_key
        if session_key:
            UserSession.objects.create(
                user=user,
                session_key=session_key,
                ip_address=ip_address,
                user_agent=user_agent
            )
        
        logger.info(f"Successful login for user {user.username} from {ip_address}")
        
        return Response(serializer.validated_data, status=status.HTTP_200_OK)


@extend_schema(
    summary="Logout and blacklist token",
    description="Logout user and add refresh token to blacklist",
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """
    Logout user and blacklist the refresh token.
    """
    try:
        refresh_token = request.data.get("refresh_token")
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Update user session status
        user = request.user
        user.is_active_session = False
        user.save(update_fields=['is_active_session'])
        
        # Mark sessions as inactive
        UserSession.objects.filter(
            user=user,
            is_active=True
        ).update(
            is_active=False,
            logout_time=timezone.now()
        )
        
        logger.info(f"User {user.username} logged out from {get_client_ip(request)}")
        
        return Response(
            {"message": "Successfully logged out"},
            status=status.HTTP_200_OK
        )
    except TokenError:
        return Response(
            {"error": "Invalid token"},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema(
    summary="Get current user profile",
    description="Retrieve authenticated user's profile information",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def profile_view(request):
    """
    Get current user's profile information.
    """
    serializer = UserProfileSerializer(request.user)
    return Response(serializer.data)


@extend_schema(
    summary="Update user profile",
    description="Update authenticated user's profile information",
)
@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def update_profile_view(request):
    """
    Update current user's profile information.
    """
    serializer = UserProfileSerializer(
        request.user,
        data=request.data,
        partial=request.method == 'PATCH'
    )
    
    if serializer.is_valid():
        serializer.save()
        logger.info(f"User {request.user.username} updated profile")
        return Response(serializer.data)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Change password",
    description="Change authenticated user's password",
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def change_password_view(request):
    """
    Change user's password.
    """
    serializer = ChangePasswordSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        
        # Check current password
        if not user.check_password(serializer.validated_data['current_password']):
            return Response(
                {"current_password": ["Current password is incorrect"]},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(serializer.validated_data['new_password'])
        user.save()
        
        logger.info(f"User {user.username} changed password")
        
        return Response(
            {"message": "Password changed successfully"},
            status=status.HTTP_200_OK
        )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(
    summary="Get user sessions",
    description="Retrieve user's active and recent sessions",
)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_sessions_view(request):
    """
    Get user's session information.
    """
    sessions = UserSession.objects.filter(
        user=request.user
    ).order_by('-login_time')[:10]
    
    session_data = []
    for session in sessions:
        session_data.append({
            'id': session.id,
            'ip_address': session.ip_address,
            'user_agent': session.user_agent,
            'login_time': session.login_time,
            'last_activity': session.last_activity,
            'is_active': session.is_active,
            'logout_time': session.logout_time,
        })
    
    return Response({
        'sessions': session_data,
        'active_sessions_count': sessions.filter(is_active=True).count()
    })


@extend_schema(
    summary="Terminate session",
    description="Terminate a specific user session",
)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def terminate_session_view(request, session_id):
    """
    Terminate a specific user session.
    """
    try:
        session = UserSession.objects.get(
            id=session_id,
            user=request.user,
            is_active=True
        )
        
        session.is_active = False
        session.logout_time = timezone.now()
        session.save()
        
        logger.info(f"User {request.user.username} terminated session {session_id}")
        
        return Response(
            {"message": "Session terminated successfully"},
            status=status.HTTP_200_OK
        )
    
    except UserSession.DoesNotExist:
        return Response(
            {"error": "Session not found or already terminated"},
            status=status.HTTP_404_NOT_FOUND
        )