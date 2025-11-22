from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='job_postings.index'),
    path('search/', views.search, name='job_postings.search'),
    path('recommendations/', views.recommendations, name='job_postings.recommendations'),
    path('map/', views.job_map, name='job_postings.map'),
    path('<int:id>/candidates/', views.candidate_recommendations, name='job_postings.candidate_recommendations'),
    path('<int:id>/', views.show, name='job_postings.show'),
    path('<int:id>/apply/', views.apply_to_job, name='job_postings.apply'),
    path('create/', views.create, name='job_postings.create'),
    path('<int:id>/edit/', views.edit, name='job_postings.edit'),
    path('<int:id>/delete/', views.delete, name='job_postings.delete'),
    path('<int:id>/manage-applications/', views.manage_applications, name='job_postings.manage_applications'),
    path('<int:id>/applicant-locations/', views.applicant_location_map, name='job_postings.applicant_location_map'),
    path('update-application-status/<int:application_id>/', views.update_application_status, name='job_postings.update_application_status'),
    # Pipeline URLs
    path('<int:id>/pipeline/', views.pipeline, name='job_postings.pipeline'),
    path('update-pipeline-status/<int:application_id>/', views.update_pipeline_status, name='job_postings.update_pipeline_status'),
    path('update-application-notes/<int:application_id>/', views.update_application_notes, name='job_postings.update_application_notes'),
    path('job/<int:job_id>/applicant/<int:user_id>/', views.view_applicant_profile, name='view_applicant_profile'),
] 