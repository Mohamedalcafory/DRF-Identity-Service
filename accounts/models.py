"""
Custom User model and related models for authentication and authorization.
"""
from django.contrib.auth.models import AbstractUser
from django.db import models


class Role(models.TextChoices):
    """User roles with different permission levels."""
    ADMIN = 'admin', 'Administrator'
    MANAGER = 'manager', 'Manager'
    USER = 'user', 'User'


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds role-based access control and additional profile fields.
    """
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
        help_text="User's role determining their permissions"
    )
    
    employee_id = models.CharField(
        max_length=50,
        unique=True,
        null=True,
        blank=True,
        help_text="Employee ID from HR system"
    )
    
    department = models.CharField(
        max_length=100,
        blank=True,
        help_text="User's department"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    
    is_active_session = models.BooleanField(
        default=False,
        help_text="Whether user has an active session"
    )
    
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of last login"
    )
    
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this datetime"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        indexes = [
            models.Index(fields=['role']),
            models.Index(fields=['employee_id']),
            models.Index(fields=['is_active']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        """Check if user has admin role."""
        return self.role == Role.ADMIN
    
    @property
    def is_manager(self):
        """Check if user has manager role."""
        return self.role == Role.MANAGER
    
    @property
    def is_user(self):
        """Check if user has user role."""
        return self.role == Role.USER
    
    def can_access_audit_logs(self):
        """Check if user can access audit logs."""
        return self.role in [Role.ADMIN, Role.MANAGER]
    
    def can_manage_users(self):
        """Check if user can manage other users."""
        return self.role == Role.ADMIN
    
    def can_view_reports(self):
        """Check if user can view reports."""
        return self.role in [Role.ADMIN, Role.MANAGER]
    
    def can_modify_settings(self):
        """Check if user can modify system settings."""
        return self.role == Role.ADMIN


class UserSession(models.Model):
    """
    Track user sessions for security and audit purposes.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sessions'
    )
    
    session_key = models.CharField(
        max_length=40,
        unique=True,
        help_text="Django session key"
    )
    
    ip_address = models.GenericIPAddressField(
        help_text="IP address of the session"
    )
    
    user_agent = models.TextField(
        blank=True,
        help_text="Browser user agent string"
    )
    
    login_time = models.DateTimeField(
        auto_now_add=True,
        help_text="When the session started"
    )
    
    last_activity = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether the session is currently active"
    )
    
    logout_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the session ended"
    )
    
    class Meta:
        db_table = 'user_sessions'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['session_key']),
            models.Index(fields=['login_time']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.ip_address} ({self.login_time})"


