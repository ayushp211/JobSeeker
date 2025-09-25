from django.urls import path
from . import views

urlpatterns = [
    path('', views.profile, name='user_profiles.profile'),
    path('profile/edit-headline/', views.edit_headline, name='user_profiles.edit_headline'),
    path('profile/add-experience/', views.add_experience, name='user_profiles.add_experience'),
    path('profile/add-education/', views.add_education, name='user_profiles.add_education'),
    path('profile/manage-skills/', views.manage_skills, name='user_profiles.manage_skills'),
    path('profile/delete-experience/<int:experience_id>/', views.delete_experience, name='user_profiles.delete_experience'),
    path('profile/delete-education/<int:education_id>/', views.delete_education, name='user_profiles.delete_education'),
    path('profile/add-link/', views.add_link, name='user_profiles.add_link'),
    path('profile/delete-link/<int:link_id>/', views.delete_link, name='user_profiles.delete_link'),
] 