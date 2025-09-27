from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404, JsonResponse
from django.db.models import Q
from django.db import IntegrityError
from .models import Job, JobApplication
from .forms import JobForm, JobSearchForm, JobApplicationForm

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
        applications = applications.filter(status=status_filter)
    
    applications = applications.order_by('-applied_at')
    
    return render(request, 'job_postings/manage_applications.html', {
        'job': job,
        'applications': applications,
        'status_filter': status_filter,
        'status_choices': JobApplication.STATUS_CHOICES,
    })

@login_required
def update_application_status(request, application_id):
    """
    Updates the status of a job application.
    Only the recruiter who posted the job can update application status.
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
        
        new_status = request.POST.get('status')
        
        if new_status in dict(JobApplication.STATUS_CHOICES):
            application.status = new_status
            application.save()
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': True, 
                    'message': f'Application status updated to {application.get_status_display()}',
                    'new_status': new_status,
                    'status_display': application.get_status_display()
                })
            
            messages.success(request, f'Application status updated to {application.get_status_display()}')
        else:
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({'success': False, 'error': 'Invalid status'})
            messages.error(request, 'Invalid status')
    
    return redirect('job_postings.manage_applications', id=application.job.id)
