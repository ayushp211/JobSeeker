from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JobSeekerProfile, WorkExperience, Education, Link, Skill
from user_accounts.models import UserProfile
from job_postings.models import JobApplication
from .forms import HeadlineForm, WorkExperienceForm, EducationForm, SkillsForm, LinkForm

@login_required
def profile(request):
    """
    Displays the user's profile based on their user type.
    - If the user is a 'job_seeker', it displays their detailed professional profile.
    - If the user is a 'recruiter', it shows a placeholder page.
    """
    user_profile = get_object_or_404(UserProfile, user=request.user)

    if user_profile.user_type == 'job_seeker':
        job_seeker_profile, created = JobSeekerProfile.objects.get_or_create(user=request.user)
        
        work_experience = job_seeker_profile.experience.all()
        education = job_seeker_profile.education.all()
        skills = job_seeker_profile.skills.all()
        links = job_seeker_profile.links.all()
        applications = JobApplication.objects.filter(applicant=request.user).order_by('-applied_at')

        template_data = {
            'profile': job_seeker_profile,
            'experiences': work_experience,
            'educations': education,
            'skills': skills,
            'links': links,
            'applications': applications,
        }

        return render(request, 'user_profiles/profile.html', {'template_data': template_data})
    
    elif user_profile.user_type == 'recruiter':
        return render(request, 'user_profiles/recruiter_placeholder.html')

@login_required
def edit_headline(request):
    """
    View to edit the user's headline.
    """
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        form = HeadlineForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('user_profiles.profile')
    else:
        form = HeadlineForm(instance=profile)
    return render(request, 'user_profiles/edit_headline.html', {'form': form})

@login_required
def add_experience(request):
    """
    View to add a new work experience entry.
    """
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        form = WorkExperienceForm(request.POST)
        if form.is_valid():
            experience = form.save(commit=False)
            experience.profile = profile
            experience.save()
            return redirect('user_profiles.profile')
    else:
        form = WorkExperienceForm()
    return render(request, 'user_profiles/add_experience.html', {'form': form})

@login_required
def delete_experience(request, experience_id):
    experience = get_object_or_404(WorkExperience, id=experience_id, profile__user=request.user)
    if request.method == 'POST':
        experience = get_object_or_404(WorkExperience, id=experience_id, profile__user=request.user)
        experience.delete()
    return redirect('user_profiles.profile')

@login_required
def add_education(request):
    """
    View to add a new education entry.
    """
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        form = EducationForm(request.POST)
        if form.is_valid():
            education = form.save(commit=False)
            education.profile = profile
            education.save()
            return redirect('user_profiles.profile')
    else:
        form = EducationForm()
    return render(request, 'user_profiles/add_education.html', {'form': form})

@login_required
def delete_education(request, education_id):
    education = get_object_or_404(Education, id=education_id, profile__user=request.user)
    if request.method == 'POST':
        education = get_object_or_404(Education, id=education_id, profile__user=request.user)
        education.delete()
    return redirect('user_profiles.profile')

@login_required
def manage_skills(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        form = SkillsForm(request.POST)
        if form.is_valid():
            # Clear existing skills first to handle deletions
            profile.skills.clear()
            skill_names = [name.strip() for name in form.cleaned_data['skills'].split(',') if name.strip()]
            
            for skill_name in skill_names:
                # Get or create the skill object, case-insensitive, to avoid duplicates
                skill, created = Skill.objects.get_or_create(name__iexact=skill_name, defaults={'name': skill_name})
                profile.skills.add(skill)
    
            return redirect('user_profiles.profile')
    else:
        # Pre-populate the form with the user's current skills joined into a string
        current_skills = ", ".join([skill.name for skill in profile.skills.all()])
        form = SkillsForm(initial={'skills': current_skills})
        
    return render(request, 'user_profiles/manage_skills.html', {'form': form})

@login_required
def add_link(request):
    """
    View to add a new link.
    """
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        form = LinkForm(request.POST)
        if form.is_valid():
            link = form.save(commit=False)
            link.profile = profile
            link.save()
            return redirect('user_profiles.profile')
    else:
        form = LinkForm()
    return render(request, 'user_profiles/add_link.html', {'form': form})

@login_required
def delete_link(request, link_id):
    """
    Deletes a link entry without a confirmation page.
    """
    if request.method == 'POST':
        link = get_object_or_404(Link, id=link_id, profile__user=request.user)
        link.delete()
    return redirect('user_profiles.profile')
