from django.urls import path
from . import views

urlpatterns = [
    path('', views.inbox, name='messaging.inbox'),
    path('conversation/<int:conversation_id>/', views.conversation_detail, name='messaging.conversation_detail'),
    path('start/<int:user_id>/', views.start_conversation, name='messaging.start_conversation'),
    path('start/<int:user_id>/job/<int:job_id>/', views.start_conversation, name='messaging.start_conversation_with_job'),
    path('send-message/<int:conversation_id>/', views.send_message_ajax, name='messaging.send_message_ajax'),
    path('unread-count/', views.get_unread_count, name='messaging.unread_count'),
    path('close/<int:conversation_id>/', views.close_conversation, name='messaging.close_conversation'),
]
