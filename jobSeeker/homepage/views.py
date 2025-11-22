from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.db.models import Q
import csv
from io import StringIO
from datetime import datetime

from user_accounts.models import UserProfile
from user_profiles.models import JobSeekerProfile
from job_postings.models import Job, JobApplication, ApplicationStatus
from messaging.models import Conversation, Message

# Create your views here.

def index(request):
    template_data = {'title': 'Job Seeker Platform'}
    return render(request, 'homepage/index.html', {'template_data': template_data})

def about(request):
    template_data = {'title': 'About'}
    return render(request, 'homepage/about.html', {'template_data': template_data})

def is_administrator(user):
    """Check if user is an administrator (staff or superuser)"""
    return user.is_authenticated and (user.is_staff or user.is_superuser)

@login_required
@user_passes_test(is_administrator)
def admin_export(request):
    """
    US#21: Administrator-facing page to select and export data as CSV for reporting.
    """
    template_data = {'title': 'Data Export - Administrator'}
    return render(request, 'homepage/admin_export.html', {'template_data': template_data})

@login_required
@user_passes_test(is_administrator)
def export_csv(request, data_type):
    """
    US#21: CSV export endpoint for various data types.
    Supports: users, jobs, applications, conversations, messages, profiles
    """
    if data_type not in ['users', 'jobs', 'applications', 'conversations', 'messages', 'profiles']:
        messages.error(request, 'Invalid export type.')
        return redirect('homepage.admin_export')
    
    # Create CSV response
    response = HttpResponse(content_type='text/csv')
    filename = f'{data_type}_export_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    writer = csv.writer(response)
    
    if data_type == 'users':
        # Export all users with their profile information
        writer.writerow([
            'User ID', 'Username', 'Email', 'First Name', 'Last Name', 
            'User Type', 'Date Joined', 'Last Login', 'Is Staff', 'Is Superuser'
        ])
        
        users = User.objects.all().select_related('userprofile').order_by('date_joined')
        for user in users:
            user_type = 'N/A'
            try:
                user_type = user.userprofile.get_user_type_display()
            except:
                pass
            
            writer.writerow([
                user.id,
                user.username,
                user.email or '',
                user.first_name or '',
                user.last_name or '',
                user_type,
                user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if user.date_joined else '',
                user.last_login.strftime('%Y-%m-%d %H:%M:%S') if user.last_login else '',
                'Yes' if user.is_staff else 'No',
                'Yes' if user.is_superuser else 'No',
            ])
    
    elif data_type == 'jobs':
        # Export all job postings
        writer.writerow([
            'Job ID', 'Title', 'Company', 'Location', 'Job Type', 'Experience Level',
            'Work Location', 'Salary Min', 'Salary Max', 'Visa Sponsorship',
            'Posted By', 'Created At', 'Updated At', 'Is Active', 'Application Count'
        ])
        
        jobs = Job.objects.all().select_related('posted_by').prefetch_related('applications').order_by('-created_at')
        for job in jobs:
            skills = ', '.join([skill.name for skill in job.skills_required.all()])
            writer.writerow([
                job.id,
                job.title,
                job.company,
                job.location,
                job.get_job_type_display(),
                job.get_experience_level_display(),
                job.get_work_location_display(),
                str(job.salary_min) if job.salary_min else '',
                str(job.salary_max) if job.salary_max else '',
                'Yes' if job.visa_sponsorship else 'No',
                job.posted_by.username,
                job.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                job.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if job.is_active else 'No',
                job.applications.count(),
            ])
    
    elif data_type == 'applications':
        # Export all job applications
        writer.writerow([
            'Application ID', 'Job ID', 'Job Title', 'Company', 'Applicant Username',
            'Applicant Email', 'Status', 'Applied At', 'Status Updated At', 'Has Notes'
        ])
        
        applications = JobApplication.objects.all().select_related(
            'job', 'applicant', 'status'
        ).order_by('-applied_at')
        
        for app in applications:
            applicant_email = app.applicant.email or ''
            writer.writerow([
                app.id,
                app.job.id,
                app.job.title,
                app.job.company,
                app.applicant.username,
                applicant_email,
                app.status.name if app.status else 'No Status',
                app.applied_at.strftime('%Y-%m-%d %H:%M:%S'),
                app.status_updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if app.notes else 'No',
            ])
    
    elif data_type == 'conversations':
        # Export all conversations
        writer.writerow([
            'Conversation ID', 'Recruiter Username', 'Job Seeker Username',
            'Job ID', 'Job Title', 'Subject', 'Created At', 'Updated At', 'Is Active',
            'Message Count', 'Latest Message At'
        ])
        
        conversations = Conversation.objects.all().select_related(
            'recruiter', 'job_seeker', 'job'
        ).prefetch_related('messages').order_by('-created_at')
        
        for conv in conversations:
            latest_message = conv.get_latest_message()
            writer.writerow([
                conv.id,
                conv.recruiter.username,
                conv.job_seeker.username,
                conv.job.id if conv.job else '',
                conv.job.title if conv.job else '',
                conv.subject,
                conv.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                conv.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if conv.is_active else 'No',
                conv.messages.count(),
                latest_message.created_at.strftime('%Y-%m-%d %H:%M:%S') if latest_message else '',
            ])
    
    elif data_type == 'messages':
        # Export all messages
        writer.writerow([
            'Message ID', 'Conversation ID', 'Sender Username', 'Recipient Username',
            'Subject', 'Content', 'Created At', 'Is Read'
        ])
        
        messages = Message.objects.all().select_related(
            'conversation', 'sender', 'conversation__recruiter', 'conversation__job_seeker'
        ).order_by('-created_at')
        
        for msg in messages:
            # Determine recipient
            if msg.sender == msg.conversation.recruiter:
                recipient = msg.conversation.job_seeker.username
            else:
                recipient = msg.conversation.recruiter.username
            
            writer.writerow([
                msg.id,
                msg.conversation.id,
                msg.sender.username,
                recipient,
                msg.conversation.subject,
                msg.content[:500],  # Limit content length
                msg.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'Yes' if msg.is_read else 'No',
            ])
    
    elif data_type == 'profiles':
        # Export job seeker profiles
        writer.writerow([
            'Profile ID', 'User ID', 'Username', 'Email', 'First Name', 'Last Name',
            'Headline', 'Preferred Location', 'Latitude', 'Longitude', 'Commute Radius',
            'Skills', 'Education Count', 'Experience Count', 'Links Count',
            'Profile Created', 'Profile Updated'
        ])
        
        profiles = JobSeekerProfile.objects.all().select_related('user').prefetch_related(
            'skills', 'education', 'experience', 'links'
        ).order_by('user__date_joined')
        
        for profile in profiles:
            skills = ', '.join([skill.name for skill in profile.skills.all()])
            writer.writerow([
                profile.id,
                profile.user.id,
                profile.user.username,
                profile.email or profile.user.email or '',
                profile.first_name or '',
                profile.last_name or '',
                profile.headline or '',
                profile.preferred_location or '',
                str(profile.latitude) if profile.latitude else '',
                str(profile.longitude) if profile.longitude else '',
                str(profile.commute_radius) if profile.commute_radius else '',
                skills,
                profile.education.count(),
                profile.experience.count(),
                profile.links.count(),
                profile.user.date_joined.strftime('%Y-%m-%d %H:%M:%S') if profile.user.date_joined else '',
                profile.user.userprofile.updated_at.strftime('%Y-%m-%d %H:%M:%S') if hasattr(profile.user, 'userprofile') else '',
            ])
    
    return response
