from django.contrib import admin
from .models import Job

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
