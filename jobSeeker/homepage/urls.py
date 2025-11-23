from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='homepage.index'),
    path('about/', views.about, name='homepage.about'),
    path('data-export/', views.admin_export, name='homepage.admin_export'),
    path('data-export/<str:data_type>/', views.export_csv, name='homepage.export_csv'),
] 