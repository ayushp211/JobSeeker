from django.contrib import admin
from .models import Conversation, Message, MessageNotification

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['subject', 'recruiter', 'job_seeker', 'job', 'created_at', 'is_active']
    list_filter = ['is_active', 'created_at', 'job']
    search_fields = ['subject', 'recruiter__username', 'job_seeker__username', 'job__title']
    readonly_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']

@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'sender', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['content', 'sender__username', 'conversation__subject']
    readonly_fields = ['created_at']
    ordering = ['-created_at']

@admin.register(MessageNotification)
class MessageNotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'conversation', 'unread_count', 'last_read_at']
    list_filter = ['unread_count', 'last_read_at']
    search_fields = ['user__username', 'conversation__subject']
    readonly_fields = ['last_read_at']
    ordering = ['-last_read_at']