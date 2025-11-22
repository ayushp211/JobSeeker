from django.contrib import admin
from .models import JobSeekerProfile, WorkExperience, Education, Skill, Link, SavedCandidateSearch, SearchNotification

admin.site.register(JobSeekerProfile)
admin.site.register(WorkExperience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Link)

@admin.register(SavedCandidateSearch)
class SavedCandidateSearchAdmin(admin.ModelAdmin):
    list_display = ('name', 'recruiter', 'is_active', 'created_at', 'last_checked_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'recruiter__username')
    filter_horizontal = ('skills',)

@admin.register(SearchNotification)
class SearchNotificationAdmin(admin.ModelAdmin):
    list_display = ('saved_search', 'candidate', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('saved_search__name', 'candidate__user__username')
