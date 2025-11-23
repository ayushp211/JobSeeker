from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db.models import Q, Count
from django.db import IntegrityError
from django.utils import timezone
from collections import defaultdict
import json
from django.urls import reverse
from .models import Job, JobApplication, ApplicationStatus
from .forms import JobForm, JobSearchForm, JobApplicationForm, ApplicationStatusForm
from user_profiles.models import JobSeekerProfile
from .recommendation_service import (
    get_candidate_recommendations_for_job,
    _calculate_experience_match,
    _calculate_profile_completeness_score,
)

def index(request):
    jobs = Job.objects.filter(is_active=True)
    return render(request, 'job_postings/index.html', {'jobs': jobs})


def search(request):
    form = JobSearchForm(request.GET)
    jobs = Job.objects.filter(is_active=True)
    
    if form.is_valid():
        # Title search
        title = form.cleaned_data.get('title')
        if title:
            jobs = jobs.filter(title__icontains=title)
        
        # Location search
        location = form.cleaned_data.get('location')
        if location:
            jobs = jobs.filter(location__icontains=location)
        
        # Job type filter
        job_type = form.cleaned_data.get('job_type')
        if job_type:
            jobs = jobs.filter(job_type=job_type)
        
        # Experience level filter
        experience_level = form.cleaned_data.get('experience_level')
        if experience_level:
            jobs = jobs.filter(experience_level=experience_level)
        
        # Work location filter
        work_location = form.cleaned_data.get('work_location')
        if work_location:
            jobs = jobs.filter(work_location=work_location)
        
        # Salary range filter
        salary_min = form.cleaned_data.get('salary_min')
        if salary_min:
            jobs = jobs.filter(
                Q(salary_max__gte=salary_min) | Q(salary_max__isnull=True)
            )
        
        salary_max = form.cleaned_data.get('salary_max')
        if salary_max:
            jobs = jobs.filter(
                Q(salary_min__lte=salary_max) | Q(salary_min__isnull=True)
            )
        
        # Visa sponsorship filter
        visa_sponsorship = form.cleaned_data.get('visa_sponsorship')
        if visa_sponsorship:
            jobs = jobs.filter(visa_sponsorship=True)
        
        # Skills filter
        skills = form.cleaned_data.get('skills')
        if skills:
            jobs = jobs.filter(skills_required__in=skills).distinct()
    
    return render(request, 'job_postings/search.html', {
        'form': form,
        'jobs': jobs,
        'search_performed': any(form.cleaned_data.values()) if form.is_valid() else False
    })

def show(request, id):
    job = get_object_or_404(Job, id=id, is_active=True)
    user_has_applied = False
    application_form = None
    
    if request.user.is_authenticated:
        # Check if user has already applied
        user_has_applied = JobApplication.objects.filter(job=job, applicant=request.user).exists()
        # Only show form if user hasn't applied and is a job seeker
        if not user_has_applied and hasattr(request.user, 'userprofile') and request.user.userprofile.user_type == 'job_seeker':
            application_form = JobApplicationForm()
    
    return render(request, 'job_postings/show.html', {
        'job': job,
        'user_has_applied': user_has_applied,
        'application_form': application_form
    })

@login_required
def apply_to_job(request, id):
    job = get_object_or_404(Job, id=id, is_active=True)
    
    # Only job seekers can apply
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'job_seeker':
        if request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': False, 'error': 'Only job seekers can apply to jobs.'})
        messages.error(request, 'Only job seekers can apply to jobs.')
        return redirect('job_postings.show', id=id)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST)
        if form.is_valid():
            try:
                application = form.save(commit=False)
                application.job = job
                application.applicant = request.user
                application.save()
                
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'success': True, 'message': 'Application submitted successfully!'})
                
                messages.success(request, 'Your application has been submitted successfully!')
                return redirect('job_postings.show', id=id)
            
            except IntegrityError:
                # User already applied
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'success': False, 'error': 'You have already applied to this job.'})
                messages.error(request, 'You have already applied to this job.')
                return redirect('job_postings.show', id=id)
        else:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Please provide a valid tailored note.'})
            messages.error(request, 'Please provide a valid tailored note.')
    
    return redirect('job_postings.show', id=id)

@login_required
def create(request):
    # Check if user is a recruiter
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can post jobs.')
        return redirect('job_postings.index')
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('job_postings.show', id=job.id)
    else:
        form = JobForm()
    
    return render(request, 'job_postings/create.html', {'form': form})

@login_required
def edit(request, id):
    job = get_object_or_404(Job, id=id)
    
    # Check if user is the owner of the job and is a recruiter
    if job.posted_by != request.user:
        messages.error(request, 'You can only edit your own job postings.')
        return redirect('job_postings.show', id=id)
    
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can edit jobs.')
        return redirect('job_postings.show', id=id)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('job_postings.show', id=job.id)
    else:
        form = JobForm(instance=job)
    
    return render(request, 'job_postings/edit.html', {'form': form, 'job': job})

@login_required
def delete(request, id):
    job = get_object_or_404(Job, id=id)
    
    # Check if user is the owner of the job and is a recruiter
    if job.posted_by != request.user:
        messages.error(request, 'You can only delete your own job postings.')
        return redirect('job_postings.show', id=id)
    
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can delete jobs.')
        return redirect('job_postings.show', id=id)
    
    if request.method == 'POST':
        job.is_active = False  # Soft delete
        job.save()
        messages.success(request, 'Job posting deleted successfully!')
        return redirect('job_postings.index')
    
    return render(request, 'job_postings/delete.html', {'job': job})

@login_required
def manage_applications(request, id):
    """
    View for recruiters to manage applications for their job postings.
    """
    job = get_object_or_404(Job, id=id)
    
    # Check if user is the owner of the job and is a recruiter
    if job.posted_by != request.user:
        messages.error(request, 'You can only manage applications for your own job postings.')
        return redirect('job_postings.show', id=id)
    
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can manage applications.')
        return redirect('job_postings.show', id=id)
    
    # Get status filter from request
    status_filter = request.GET.get('status', '')
    applications = job.applications.all()
    
    if status_filter:
        applications = applications.filter(status__id=status_filter)
    
    applications = applications.order_by('-applied_at')
    
    # Get all available statuses for the filter dropdown
    all_statuses = ApplicationStatus.objects.all().order_by('order')
    
    return render(request, 'job_postings/manage_applications.html', {
        'job': job,
        'applications': applications,
        'status_filter': status_filter,
        'all_statuses': all_statuses,
    })


@login_required
def candidate_recommendations(request, id):
    """
    US#16: Recruiter-facing view to see recommended candidates for a specific job.
    Uses the candidate recommendation service and does not replace existing functionality.
    """
    job = get_object_or_404(Job, id=id)

    # Ensure only the recruiter who posted the job can view recommendations
    if job.posted_by != request.user:
        messages.error(request, 'You can only view recommendations for your own job postings.')
        return redirect('job_postings.show', id=id)

    # Ensure user is a recruiter
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view candidate recommendations.')
        return redirect('job_postings.show', id=id)

    # Build recommendations only among candidates who have actually applied
    applications = JobApplication.objects.filter(job=job).select_related('applicant')
    applied_user_ids = [app.applicant_id for app in applications]

    profiles = JobSeekerProfile.objects.filter(user_id__in=applied_user_ids)

    required_skills_qs = job.skills_required.all()
    required_skills = list(required_skills_qs)
    required_skill_names = {s.name.strip().lower() for s in required_skills}

    recommendations = []
    for profile in profiles:
        profile_skills = list(profile.skills.all())
        matching_skills = [
            skill for skill in profile_skills
            if skill.name and skill.name.strip().lower() in required_skill_names
        ]
        skill_match_count = len(matching_skills)
        total_required_skills = len(required_skills)

        # Primary factor: skill overlap
        skill_match_percentage = (
            (skill_match_count / total_required_skills) * 100
            if total_required_skills > 0 else 0
        )

        # Secondary factor: experience level compatibility
        experience_score = _calculate_experience_match(job, profile)

        # Tertiary factor: profile completeness
        completeness_score = _calculate_profile_completeness_score(profile)

        match_score = (
            skill_match_percentage * 0.7 +
            experience_score * 0.2 +
            completeness_score * 0.1
        )

        recommendations.append({
            'profile': profile,
            'match_score': match_score,
            'matching_skills': matching_skills,
            'skill_match_count': skill_match_count,
            'total_required_skills': total_required_skills,
        })

    # Sort applicants by match score, highest first
    recommendations.sort(key=lambda x: x['match_score'], reverse=True)

    return render(request, 'job_postings/candidate_recommendations.html', {
        'job': job,
        'recommendations': recommendations,
    })

@login_required
def update_application_status(request, application_id):
    """
    Updates the status of a job application.
    Only the recruiter who posted the job can update application status.
    This is kept for backward compatibility but status is now managed via pipeline.
    """
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Check if user is the recruiter who posted the job
        if application.job.posted_by != request.user:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'You can only update applications for your own job postings.'})
            messages.error(request, 'You can only update applications for your own job postings.')
            return redirect('job_postings.show', id=application.job.id)
        
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Only recruiters can update application status.'})
            messages.error(request, 'Only recruiters can update application status.')
            return redirect('job_postings.show', id=application.job.id)
        
        status_id = request.POST.get('status_id')
        
        if status_id:
            try:
                new_status = ApplicationStatus.objects.get(id=status_id)
                application.status = new_status
                application.save()
                
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({
                        'success': True, 
                        'message': f'Application status updated to {new_status.name}',
                        'new_status': new_status.id,
                        'status_display': new_status.name
                    })
                
                messages.success(request, f'Application status updated to {new_status.name}')
            except ApplicationStatus.DoesNotExist:
                if request.headers.get('Content-Type') == 'application/json':
                    return JsonResponse({'success': False, 'error': 'Invalid status'})
                messages.error(request, 'Invalid status')
        else:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'No status provided'})
            messages.error(request, 'No status provided')
    
    return redirect('job_postings.manage_applications', id=application.job.id)

@login_required
def pipeline(request, id):
    """
    Kanban board view showing applications for a specific job organized by status.
    Only accessible to recruiters who own the job.
    """
    job = get_object_or_404(Job, id=id)
    
    # Check if user is the owner of the job and is a recruiter
    if job.posted_by != request.user:
        messages.error(request, 'You can only view the pipeline for your own job postings.')
        return redirect('job_postings.show', id=id)
    
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can access the pipeline.')
        return redirect('job_postings.show', id=id)
    
    # Get all statuses ordered by their order field (fixed 5 statuses)
    statuses = ApplicationStatus.objects.all().order_by('order')
    
    # Get all applications for this specific job
    all_applications = job.applications.select_related('applicant', 'status')
    
    # Organize applications by status
    applications_by_status = defaultdict(list)
    
    for application in all_applications:
        if application.status:
            applications_by_status[application.status].append(application)
    
    return render(request, 'job_postings/pipeline.html', {
        'job': job,
        'statuses': statuses,
        'applications_by_status': dict(applications_by_status),
    })

@login_required
def update_pipeline_status(request, application_id):
    """
    AJAX endpoint to update the status of an application in the pipeline.
    Only the recruiter who posted the job can update application status.
    """
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Check if user is the recruiter who posted the job
        if application.job.posted_by != request.user:
            return JsonResponse({'success': False, 'error': 'You can only update applications for your own job postings.'})
        
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
            return JsonResponse({'success': False, 'error': 'Only recruiters can update application status.'})
        
        status_id = request.POST.get('status_id')
        
        if status_id:
            try:
                new_status = ApplicationStatus.objects.get(id=status_id)
                application.status = new_status
                application.save()
                return JsonResponse({
                    'success': True, 
                    'message': f'Application status updated to {new_status.name}'
                })
            except ApplicationStatus.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Invalid status'})
        else:
            # Setting status to null
            application.status = None
            application.save()
            return JsonResponse({
                'success': True, 
                'message': 'Application status cleared'
            })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def update_application_notes(request, application_id):
    """
    AJAX endpoint to update internal notes for an application.
    Only the recruiter who posted the job can update notes.
    """
    if request.method == 'POST':
        application = get_object_or_404(JobApplication, id=application_id)
        
        # Check if user is the recruiter who posted the job
        if application.job.posted_by != request.user:
            return JsonResponse({'success': False, 'error': 'You can only update applications for your own job postings.'})
        
        if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
            return JsonResponse({'success': False, 'error': 'Only recruiters can update application notes.'})
        
        notes = request.POST.get('notes', '')
        application.notes = notes
        application.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Notes updated successfully',
            'notes': notes
        })
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

# Admin Moderation Views

def is_admin(user):
    """Check if user is a superuser/admin"""
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    flagged_jobs = Job.objects.filter(is_flagged=True).count()
    inactive_jobs = Job.objects.filter(is_active=False).count()
    
    total_applications = JobApplication.objects.count()
    total_users = User.objects.count()
    
    recent_jobs = Job.objects.order_by('-created_at')[:5]
    flagged_jobs_list = Job.objects.filter(is_flagged=True).order_by('-flagged_at')[:5]
    
    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'flagged_jobs': flagged_jobs,
        'inactive_jobs': inactive_jobs,
        'total_applications': total_applications,
        'total_users': total_users,
        'recent_jobs': recent_jobs,
        'flagged_jobs_list': flagged_jobs_list,
    }
    
    return render(request, 'job_postings/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_moderate_jobs(request):
    """View all jobs for moderation"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')
    
    jobs = Job.objects.select_related('posted_by').annotate(
        application_count=Count('applications')
    )
    
    # Apply filters
    if status_filter == 'active':
        jobs = jobs.filter(is_active=True, is_flagged=False)
    elif status_filter == 'inactive':
        jobs = jobs.filter(is_active=False)
    elif status_filter == 'flagged':
        jobs = jobs.filter(is_flagged=True)
    
    # Apply search
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    jobs = jobs.order_by('-created_at')
    
    context = {
        'jobs': jobs,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'job_postings/admin_moderate_jobs.html', context)

@user_passes_test(is_admin)
def admin_flag_job(request, id):
    """Flag a job post for review"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Flagged by administrator')
        job.is_flagged = True
        job.flagged_reason = reason
        job.flagged_at = timezone.now()
        job.flagged_by = request.user
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been flagged for review.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return render(request, 'job_postings/admin_flag_job.html', {'job': job})

@user_passes_test(is_admin)
def admin_unflag_job(request, id):
    """Remove flag from a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job.is_flagged = False
        job.flagged_reason = ''
        job.flagged_at = None
        job.flagged_by = None
        job.save()
        
        messages.success(request, f'Flag removed from job "{job.title}".')
        return redirect('job_postings.admin_moderate_jobs')
    
    return redirect('job_postings.admin_moderate_jobs')

@user_passes_test(is_admin)
def admin_deactivate_job(request, id):
    """Deactivate a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job.is_active = False
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been deactivated.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return redirect('job_postings.admin_moderate_jobs')

@user_passes_test(is_admin)
def admin_activate_job(request, id):
    """Activate a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job.is_active = True
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been activated.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return redirect('job_postings.admin_moderate_jobs')

@user_passes_test(is_admin)
def admin_delete_job(request, id):
    """Permanently delete a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        
        messages.success(request, f'Job "{job_title}" has been permanently deleted.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return render(request, 'job_postings/admin_delete_job.html', {'job': job})

@login_required
def view_applicant_profile(request, job_id, user_id): # Updated function signature
    """
    Allows a recruiter to view the profile of a job seeker who has
    applied to one of their jobs.
    """
    job = get_object_or_404(Job, id=job_id, posted_by=request.user)
    has_applied_to_this_job = JobApplication.objects.filter(
        job=job,
        applicant_id=user_id
    ).exists()

    if not has_applied_to_this_job:
        messages.error(request, 'This user has not applied to your job posting.')
        return redirect('job_postings.manage_applications', id=job.id)

    profile = get_object_or_404(JobSeekerProfile, user_id=user_id)
    
    context = {
        'profile': profile,
        'job': job,
    }
    
    return render(request, 'job_postings/applicant_profile.html', context)

@login_required
def recommendations(request):
    """
    View for job seekers to see job recommendations based on their skills.
    """
    # Only job seekers can access recommendations
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'job_seeker':
        messages.error(request, 'Only job seekers can view job recommendations.')
        return redirect('job_postings.index')
    
    # Get the job seeker's profile and skills
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
        user_skills = profile.skills.all()
    except JobSeekerProfile.DoesNotExist:
        messages.error(request, 'Please complete your profile to get job recommendations.')
        return redirect('user_profiles.profile')
    
    if not user_skills.exists():
        messages.info(request, 'Add skills to your profile to get personalized job recommendations.')
        return redirect('user_profiles.profile')
    
    # Get jobs that require skills matching the user's skills
    recommended_jobs = Job.objects.filter(
        is_active=True,
        skills_required__in=user_skills
    ).distinct()
    
    # Exclude jobs the user has already applied to
    applied_job_ids = JobApplication.objects.filter(
        applicant=request.user
    ).values_list('job_id', flat=True)
    recommended_jobs = recommended_jobs.exclude(id__in=applied_job_ids)
    
    # Order by number of matching skills (descending) and then by creation date
    jobs_with_match_count = []
    for job in recommended_jobs:
        matching_skills = job.skills_required.filter(id__in=user_skills.values_list('id', flat=True))
        match_count = matching_skills.count()
        jobs_with_match_count.append({
            'job': job,
            'match_count': match_count,
            'matching_skills': matching_skills
        })
    
    # Sort by match count (descending) and then by creation date
    jobs_with_match_count.sort(key=lambda x: (-x['match_count'], -x['job'].created_at.timestamp()))
    
    return render(request, 'job_postings/recommendations.html', {
        'recommended_jobs': jobs_with_match_count,
        'user_skills': user_skills
    })

@login_required
def applicant_location_map(request, id):
    """
    US#18: Recruiter-facing view to see clusters of applicants by location on a map.
    Shows where applicants for a specific job are located, with clustering for better visualization.
    """
    job = get_object_or_404(Job, id=id)
    
    # Check if user is the owner of the job and is a recruiter
    if job.posted_by != request.user:
        messages.error(request, 'You can only view applicant locations for your own job postings.')
        return redirect('job_postings.show', id=id)
    
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view applicant location maps.')
        return redirect('job_postings.show', id=id)
    
    # Get all applications for this job
    applications = JobApplication.objects.filter(job=job).select_related('applicant')
    
    # Get applicant profiles with location data
    applicant_data = []
    for application in applications:
        try:
            profile = JobSeekerProfile.objects.get(user=application.applicant)
            # Only include applicants with valid location data
            if profile.latitude and profile.longitude:
                applicant_data.append({
                    'application_id': application.id,
                    'user_id': application.applicant.id,
                    'name': profile.first_name and profile.last_name 
                            and f"{profile.first_name} {profile.last_name}" 
                            or application.applicant.get_full_name() 
                            or application.applicant.username,
                    'email': profile.email or application.applicant.email or 'No email',
                    'location': profile.preferred_location or 'Location not specified',
                    'latitude': float(profile.latitude),
                    'longitude': float(profile.longitude),
                    'applied_at': application.applied_at.strftime('%Y-%m-%d %H:%M'),
                    'status': application.status.name if application.status else 'No Status',
                    'status_color': application.status.color if application.status else '#6c757d',
                })
        except JobSeekerProfile.DoesNotExist:
            # Skip applicants without profiles
            continue
    
    return render(request, 'job_postings/applicant_location_map.html', {
        'job': job,
        'applicants_json': json.dumps(applicant_data),
        'applicants_count': len(applicant_data),
        'total_applications': applications.count(),
    })

@login_required
def job_map(request):
    """
    Interactive map view for job seekers to see job postings on a map.
    Jobs are filtered based on the user's commute radius preference.
    """
    # Only job seekers can access the map view
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'job_seeker':
        messages.error(request, 'Only job seekers can view the job map.')
        return redirect('job_postings.index')
    
    # Get the job seeker's profile
    try:
        profile = JobSeekerProfile.objects.get(user=request.user)
    except JobSeekerProfile.DoesNotExist:
        profile = None
    
    # Get all active jobs that have coordinates
    jobs = Job.objects.filter(
        is_active=True,
        latitude__isnull=False,
        longitude__isnull=False
    ).select_related('posted_by')
    
    # Helper function to calculate distance between two points using Haversine formula
    def calculate_distance(lat1, lon1, lat2, lon2):
        """Calculate distance in miles between two coordinates"""
        from math import radians, sin, cos, sqrt, atan2
        
        R = 3959  # Earth's radius in miles
        
        lat1_rad = radians(float(lat1))
        lon1_rad = radians(float(lon1))
        lat2_rad = radians(float(lat2))
        lon2_rad = radians(float(lon2))
        
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        a = sin(dlat / 2)**2 + cos(lat1_rad) * cos(lat2_rad) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        
        return R * c
    
    # Convert jobs to JSON for JavaScript
    jobs_data = []
    user_location = None
    commute_radius = None
    
    # Check if user has set commute preferences
    if profile and profile.preferred_location and profile.latitude and profile.longitude:
        user_location = {
            'latitude': float(profile.latitude),
            'longitude': float(profile.longitude),
            'address': profile.preferred_location
        }
        commute_radius = float(profile.commute_radius)
        
        # Filter jobs by distance
        filtered_jobs = []
        for job in jobs:
            distance = calculate_distance(
                profile.latitude,
                profile.longitude,
                job.latitude,
                job.longitude
            )
            if distance <= commute_radius:
                filtered_jobs.append((job, distance))
        
        # Convert filtered jobs to JSON with distance info
        for job, distance in filtered_jobs:
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'latitude': float(job.latitude),
                'longitude': float(job.longitude),
                'job_type': job.get_job_type_display(),
                'experience_level': job.get_experience_level_display(),
                'work_location': job.get_work_location_display(),
                'url': reverse('job_postings.show', args=[job.id]),
                'distance': round(distance, 1)
            })
    else:
        # No commute preferences set, show all jobs
        for job in jobs:
            jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'latitude': float(job.latitude),
                'longitude': float(job.longitude),
                'job_type': job.get_job_type_display(),
                'experience_level': job.get_experience_level_display(),
                'work_location': job.get_work_location_display(),
                'url': reverse('job_postings.show', args=[job.id])
            })
    
    # Also prepare all jobs (unfiltered) for toggle functionality
    all_jobs_data = []
    if user_location and commute_radius:
        # If user has preferences, also send all jobs for toggle
        for job in jobs:
            distance = calculate_distance(
                profile.latitude,
                profile.longitude,
                job.latitude,
                job.longitude
            )
            all_jobs_data.append({
                'id': job.id,
                'title': job.title,
                'company': job.company,
                'location': job.location,
                'latitude': float(job.latitude),
                'longitude': float(job.longitude),
                'job_type': job.get_job_type_display(),
                'experience_level': job.get_experience_level_display(),
                'work_location': job.get_work_location_display(),
                'url': reverse('job_postings.show', args=[job.id]),
                'distance': round(distance, 1)
            })
    
    return render(request, 'job_postings/map.html', {
        'jobs_json': json.dumps(jobs_data),
        'all_jobs_json': json.dumps(all_jobs_data) if all_jobs_data else json.dumps(jobs_data),
        'jobs_count': len(jobs_data),
        'all_jobs_count': len(all_jobs_data) if all_jobs_data else len(jobs_data),
        'user_location': json.dumps(user_location) if user_location else 'null',
        'commute_radius': commute_radius,
        'has_commute_filter': bool(user_location and commute_radius)
    })

# ============ Admin Moderation Views ============

def is_admin(user):
    """Check if user is a superuser/admin"""
    return user.is_authenticated and user.is_superuser

@user_passes_test(is_admin)
def admin_dashboard(request):
    """Admin dashboard with statistics"""
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True).count()
    flagged_jobs = Job.objects.filter(is_flagged=True).count()
    inactive_jobs = Job.objects.filter(is_active=False).count()
    
    total_applications = JobApplication.objects.count()
    total_users = User.objects.count()
    
    recent_jobs = Job.objects.select_related('posted_by').order_by('-created_at')[:5]
    flagged_jobs_list = Job.objects.filter(is_flagged=True).select_related('posted_by', 'flagged_by').order_by('-flagged_at')[:5]
    
    context = {
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'flagged_jobs': flagged_jobs,
        'inactive_jobs': inactive_jobs,
        'total_applications': total_applications,
        'total_users': total_users,
        'recent_jobs': recent_jobs,
        'flagged_jobs_list': flagged_jobs_list,
    }
    
    return render(request, 'job_postings/admin_dashboard.html', context)

@user_passes_test(is_admin)
def admin_moderate_jobs(request):
    """View all jobs for moderation"""
    # Get filter parameters
    status_filter = request.GET.get('status', 'all')
    search_query = request.GET.get('q', '')
    
    jobs = Job.objects.select_related('posted_by').annotate(
        application_count=Count('applications')
    )
    
    # Apply filters
    if status_filter == 'active':
        jobs = jobs.filter(is_active=True, is_flagged=False)
    elif status_filter == 'inactive':
        jobs = jobs.filter(is_active=False)
    elif status_filter == 'flagged':
        jobs = jobs.filter(is_flagged=True)
    
    # Apply search
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(company__icontains=search_query) |
            Q(location__icontains=search_query)
        )
    
    jobs = jobs.order_by('-created_at')
    
    context = {
        'jobs': jobs,
        'status_filter': status_filter,
        'search_query': search_query,
    }
    
    return render(request, 'job_postings/admin_moderate_jobs.html', context)

@user_passes_test(is_admin)
def admin_flag_job(request, id):
    """Flag a job post for review"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', 'Flagged by administrator')
        job.is_flagged = True
        job.flagged_reason = reason
        job.flagged_at = timezone.now()
        job.flagged_by = request.user
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been flagged for review.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return render(request, 'job_postings/admin_flag_job.html', {'job': job})

@user_passes_test(is_admin)
def admin_unflag_job(request, id):
    """Remove flag from a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job.is_flagged = False
        job.flagged_reason = ''
        job.flagged_at = None
        job.flagged_by = None
        job.save()
        
        messages.success(request, f'Flag removed from job "{job.title}".')
        return redirect('job_postings.admin_moderate_jobs')
    
    return redirect('job_postings.admin_moderate_jobs')

@user_passes_test(is_admin)
def admin_deactivate_job(request, id):
    """Deactivate a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job.is_active = False
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been deactivated.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return redirect('job_postings.admin_moderate_jobs')

@user_passes_test(is_admin)
def admin_activate_job(request, id):
    """Activate a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job.is_active = True
        job.save()
        
        messages.success(request, f'Job "{job.title}" has been activated.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return redirect('job_postings.admin_moderate_jobs')

@user_passes_test(is_admin)
def admin_delete_job(request, id):
    """Permanently delete a job post"""
    job = get_object_or_404(Job, id=id)
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        
        messages.success(request, f'Job "{job_title}" has been permanently deleted.')
        return redirect('job_postings.admin_moderate_jobs')
    
    return render(request, 'job_postings/admin_delete_job.html', {'job': job})