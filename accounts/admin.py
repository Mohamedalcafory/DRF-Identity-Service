from django.contrib import admin
from .models import User, UserSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'role', 'is_active', 'is_staff', 'created_at'
    )
    list_filter = ('role', 'is_active', 'is_staff', 'is_superuser')
    search_fields = ('username', 'email', 'employee_id')
    readonly_fields = ('last_login', 'date_joined', 'created_at', 'updated_at')


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'ip_address', 'is_active', 'login_time', 'logout_time'
    )
    list_filter = ('is_active',)
    search_fields = ('user__username', 'ip_address', 'session_key')


