from django.contrib import admin
from .models import UserProfile

# Register your models here.

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'user_type', 'created_at']
    list_filter = ['user_type', 'created_at']
    search_fields = ['user__username', 'user__email']
