from django.contrib import admin
from .models import Job, JobApplication

# Register your models here.

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'location', 'job_type', 'posted_by', 'created_at', 'is_active']
    list_filter = ['job_type', 'experience_level', 'is_active', 'created_at']
    search_fields = ['title', 'company', 'location', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'company', 'location', 'job_type', 'experience_level')
        }),
        ('Salary Information', {
            'fields': ('salary_min', 'salary_max'),
            'classes': ('collapse',)
        }),
        ('Job Details', {
            'fields': ('description', 'requirements')
        }),
        ('Management', {
            'fields': ('posted_by', 'is_active', 'created_at', 'updated_at')
        })
    )

@admin.register(JobApplication)
class JobApplicationAdmin(admin.ModelAdmin):
    list_display = ['job', 'applicant', 'applied_at']
    list_filter = ['applied_at', 'job__company']
    search_fields = ['job__title', 'job__company', 'applicant__username', 'applicant__first_name', 'applicant__last_name']
    readonly_fields = ['applied_at']
    
    fieldsets = (
        ('Application Details', {
            'fields': ('job', 'applicant', 'applied_at')
        }),
        ('Cover Note', {
            'fields': ('cover_note',)
        })
    )
