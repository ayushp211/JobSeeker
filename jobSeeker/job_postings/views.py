from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from django.db.models import Q
from .models import Job
from .forms import JobForm, JobSearchForm

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
    return render(request, 'job_postings/show.html', {'job': job})

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
