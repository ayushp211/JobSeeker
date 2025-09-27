from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='job_postings.index'),
    path('search/', views.search, name='job_postings.search'),
    path('<int:id>/', views.show, name='job_postings.show'),
    path('<int:id>/apply/', views.apply_to_job, name='job_postings.apply'),
    path('create/', views.create, name='job_postings.create'),
    path('<int:id>/edit/', views.edit, name='job_postings.edit'),
    path('<int:id>/delete/', views.delete, name='job_postings.delete'),
    path('<int:id>/manage-applications/', views.manage_applications, name='job_postings.manage_applications'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='job_postings.update_application_status'),
] 