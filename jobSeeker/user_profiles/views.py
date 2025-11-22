from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from .models import JobSeekerProfile, WorkExperience, Education, Link, Skill
from user_accounts.models import UserProfile
from job_postings.models import JobApplication, ApplicationStatus
from .forms import HeadlineForm, WorkExperienceForm, EducationForm, SkillsForm, LinkForm, ProfilePrivacyForm, CandidateSearchForm, LocationForm, CommutePreferencesForm

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
        # Get status filter from request
        status_filter = request.GET.get('status', '')
        applications = JobApplication.objects.filter(applicant=request.user)
        
        if status_filter:
            applications = applications.filter(status__id=status_filter)
        
        applications = applications.order_by('-applied_at')
        
        # Get all available statuses for the filter dropdown
        all_statuses = ApplicationStatus.objects.all().order_by('order')

        privacy_form = ProfilePrivacyForm(instance=job_seeker_profile)

        template_data = {
            'profile': job_seeker_profile,
            'experiences': work_experience,
            'educations': education,
            'skills': skills,
            'links': links,
            'applications': applications,
            'status_filter': status_filter,
            'all_statuses': all_statuses,
            'privacy_form': privacy_form,
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

@login_required
def manage_privacy(request):
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        form = ProfilePrivacyForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Your privacy settings have been updated successfully.')
        else:
            messages.error(request, 'There was an error updating your settings.')
    return redirect('user_profiles.profile')

@login_required
def edit_commute_preferences(request):
    """
    View to edit the user's commute preferences (location and radius).
    """
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    
    if request.method == 'POST':
        form = CommutePreferencesForm(request.POST, instance=profile)
        if form.is_valid():
            profile = form.save(commit=False)
            # Geocode the preferred location if it was changed
            if 'preferred_location' in form.changed_data and profile.preferred_location:
                profile.geocode_preferred_location()
            profile.save()
            messages.success(request, 'Your commute preferences have been updated successfully.')
            return redirect('user_profiles.profile')
        else:
            messages.error(request, 'There was an error updating your commute preferences.')
    else:
        form = CommutePreferencesForm(instance=profile)
    
    return render(request, 'user_profiles/edit_commute_preferences.html', {'form': form, 'profile': profile})

@login_required
def search_candidates(request):
    """
    View for recruiters to search for job seekers by skills, location, and projects.
    """
    # Only recruiters can search for candidates
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can search for candidates.')
        return redirect('homepage.index')
    
    form = CandidateSearchForm(request.GET)
    profiles = JobSeekerProfile.objects.all()
    search_performed = False
    
    if form.is_valid():
        # Get all job seeker profiles (respect privacy settings)
        profiles = profiles.filter(user__userprofile__user_type='job_seeker')
        search_performed = any(form.cleaned_data.values())
        
        # Filter by skills
        skills = form.cleaned_data.get('skills')
        if skills:
            profiles = profiles.filter(skills__in=skills).distinct()
        
        # Filter by location (search in work experience location)
        location = form.cleaned_data.get('location')
        if location:
            profiles = profiles.filter(
                Q(email__icontains=location) |
                Q(experience__location__icontains=location)
            ).distinct()
        
        # Filter by project keywords (search in work experience descriptions)
        project_keywords = form.cleaned_data.get('project_keywords')
        if project_keywords:
            profiles = profiles.filter(
                Q(experience__description__icontains=project_keywords) |
                Q(experience__title__icontains=project_keywords)
            ).distinct()
    
    # Calculate match scores for each profile
    profiles_with_scores = []
    for profile in profiles:
        match_score = 0
        matched_criteria = []
        
        if form.is_valid():
            skills = form.cleaned_data.get('skills')
            location = form.cleaned_data.get('location')
            project_keywords = form.cleaned_data.get('project_keywords')
            
            if skills:
                matching_skills = profile.skills.filter(id__in=[s.id for s in skills])
                if matching_skills.exists():
                    match_score += matching_skills.count()
                    matched_criteria.append(f"{matching_skills.count()} skill match(es)")
            
            if location:
                # Check if location matches in email or work experience
                if profile.email and location.lower() in profile.email.lower():
                    match_score += 1
                    matched_criteria.append("Location match")
                if profile.experience.filter(location__icontains=location).exists():
                    match_score += 1
                    matched_criteria.append("Location match")
            
            if project_keywords:
                if profile.experience.filter(
                    Q(description__icontains=project_keywords) |
                    Q(title__icontains=project_keywords)
                ).exists():
                    match_score += 1
                    matched_criteria.append("Project match")
        
        profiles_with_scores.append({
            'profile': profile,
            'match_score': match_score,
            'matched_criteria': matched_criteria
        })
    
    # Sort by match score (descending)
    profiles_with_scores.sort(key=lambda x: x['match_score'], reverse=True)
    
    return render(request, 'user_profiles/search_candidates.html', {
        'form': form,
        'profiles_with_scores': profiles_with_scores,
        'search_performed': search_performed
    })

@login_required
def view_public_profile(request, user_id):
    """
    Allows recruiters to view a job seeker's public profile.
    """
    # Only recruiters can view public profiles
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view candidate profiles.')
        return redirect('homepage.index')
    
    profile_user = get_object_or_404(UserProfile, user_id=user_id)
    
    if profile_user.user_type != 'job_seeker':
        messages.error(request, 'This profile is not available.')
        return redirect('user_profiles.search_candidates')
    
    job_seeker_profile = get_object_or_404(JobSeekerProfile, user_id=user_id)
    
    return render(request, 'user_profiles/public_profile.html', {
        'profile': job_seeker_profile
    })

@login_required
def set_location(request):
    """
    View to set the user's preferred job search location.
    Validates that the location can be geocoded before saving.
    """
    profile = get_object_or_404(JobSeekerProfile, user=request.user)
    if request.method == 'POST':
        preferred_location = request.POST.get('preferred_location', '').strip()
        latitude = request.POST.get('latitude', '').strip()
        longitude = request.POST.get('longitude', '').strip()
        
        # Validate that we have both location text and coordinates
        if not preferred_location:
            messages.error(request, 'Please enter a location.')
            return redirect('user_profiles.profile')
        
        if not latitude or not longitude:
            messages.error(request, 'Unable to geocode the location. Please click "Get Coordinates" to validate the location.')
            return redirect('user_profiles.profile')
        
        try:
            # Validate that coordinates are valid numbers
            lat_float = float(latitude)
            lng_float = float(longitude)
            
            # Validate coordinate ranges
            if not (-90 <= lat_float <= 90) or not (-180 <= lng_float <= 180):
                messages.error(request, 'Invalid coordinates. Please enter a valid location.')
                return redirect('user_profiles.profile')
            
            # Save the validated data
            profile.preferred_location = preferred_location
            profile.latitude = lat_float
            profile.longitude = lng_float
            profile.save()
            
            messages.success(request, f'Your preferred location has been set to: {preferred_location}')
        except (ValueError, TypeError):
            messages.error(request, 'Invalid location data. Please try again.')
    
    return redirect('user_profiles.profile')
