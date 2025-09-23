from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='user_profiles.profile'),
    path('edit/', views.edit_profile, name='user_profiles.edit'),
] 