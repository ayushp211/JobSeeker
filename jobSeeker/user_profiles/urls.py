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
    path('profile/manage-privacy/', views.manage_privacy, name='user_profiles.manage_privacy'),
    path('profile/edit-commute-preferences/', views.edit_commute_preferences, name='user_profiles.edit_commute_preferences'),
    path('profile/set-location/', views.set_location, name='user_profiles.set_location'),
    path('search-candidates/', views.search_candidates, name='user_profiles.search_candidates'),
    path('view-profile/<int:user_id>/', views.view_public_profile, name='user_profiles.view_public_profile'),
    path('save-search/', views.save_candidate_search, name='user_profiles.save_search'),
    path('saved-searches/', views.saved_searches, name='user_profiles.saved_searches'),
    path('saved-searches/delete/<int:search_id>/', views.delete_saved_search, name='user_profiles.delete_saved_search'),
    path('search-notifications/', views.search_notifications, name='user_profiles.search_notifications'),
    path('check-matches/', views.check_new_matches, name='user_profiles.check_matches'),
    path('check-matches/<int:search_id>/', views.check_new_matches, name='user_profiles.check_matches_search'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='user_profiles.mark_notification_read'),
] 