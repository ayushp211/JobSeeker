from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='job_postings.index'),
    path('<int:id>/', views.show, name='job_postings.show'),
    path('create/', views.create, name='job_postings.create'),
    path('<int:id>/edit/', views.edit, name='job_postings.edit'),
    path('<int:id>/delete/', views.delete, name='job_postings.delete'),
] 