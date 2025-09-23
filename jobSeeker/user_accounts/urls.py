from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='user_accounts.signup'),
    path('login/', views.login, name='user_accounts.login'),
    path('logout/', views.logout, name='user_accounts.logout'),
] 