from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import Http404
from .models import Job
from .forms import JobForm

def index(request):
    jobs = Job.objects.filter(is_active=True)
    return render(request, 'job_postings/index.html', {'jobs': jobs})

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
