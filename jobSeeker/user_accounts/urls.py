from django.urls import path
from . import views

urlpatterns = [
    path('signup/', views.signup, name='user_accounts.signup'),
    path('login/', views.login_view, name='user_accounts.login'),
    path('logout/', views.logout_view, name='user_accounts.logout'),
] 