from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.utils import timezone
from .models import JobSeekerProfile, WorkExperience, Education, Link, Skill, SavedCandidateSearch, SearchNotification
from user_accounts.models import UserProfile
from job_postings.models import JobApplication, ApplicationStatus
from .forms import HeadlineForm, WorkExperienceForm, EducationForm, SkillsForm, LinkForm, ProfilePrivacyForm, CandidateSearchForm, LocationForm, CommutePreferencesForm, SaveSearchForm

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
        
        # Filter by location (search in email, preferred_location, or work experience location)
        location = form.cleaned_data.get('location')
        if location:
            profiles = profiles.filter(
                Q(email__icontains=location) |
                Q(preferred_location__icontains=location) |
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
                # Check if location matches in email, preferred_location, or work experience
                location_lower = location.lower()
                if profile.email and location_lower in profile.email.lower():
                    match_score += 1
                    matched_criteria.append("Location match")
                elif profile.preferred_location and location_lower in profile.preferred_location.lower():
                    match_score += 1
                    matched_criteria.append("Location match")
                elif profile.experience.filter(location__icontains=location).exists():
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
    
    # Get search parameters for saving
    search_params = {
        'skills': request.GET.getlist('skills', []),
        'location': request.GET.get('location', ''),
        'project_keywords': request.GET.get('project_keywords', ''),
    }
    
    return render(request, 'user_profiles/search_candidates.html', {
        'form': form,
        'profiles_with_scores': profiles_with_scores,
        'search_performed': search_performed,
        'search_params': search_params
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

@login_required
def save_candidate_search(request):
    """
    Save the current candidate search criteria.
    """
    # Only recruiters can save searches
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can save candidate searches.')
        return redirect('homepage.index')
    
    if request.method == 'POST':
        form = SaveSearchForm(request.POST)
        if form.is_valid():
            saved_search = form.save(commit=False)
            saved_search.recruiter = request.user
            saved_search.save()
            
            # Save skills - handle both single and multiple values
            skill_ids = request.POST.getlist('skills')
            if skill_ids:
                # Filter out empty strings
                skill_ids = [sid for sid in skill_ids if sid]
                if skill_ids:
                    saved_search.skills.set(Skill.objects.filter(id__in=skill_ids))
            
            # Save location and project_keywords from form data
            location = request.POST.get('location', '').strip()
            saved_search.location = location if location else None
            
            project_keywords = request.POST.get('project_keywords', '').strip()
            saved_search.project_keywords = project_keywords if project_keywords else None
            saved_search.save()
            
            messages.success(request, f'Search "{saved_search.name}" saved successfully!')
            return redirect('user_profiles.saved_searches')
        else:
            messages.error(request, 'Please provide a name for the search.')
    
    # If GET request, redirect to search page
    return redirect('user_profiles.search_candidates')

@login_required
def saved_searches(request):
    """
    List all saved candidate searches for the recruiter.
    """
    # Only recruiters can view saved searches
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view saved searches.')
        return redirect('homepage.index')
    
    saved_searches_list = SavedCandidateSearch.objects.filter(recruiter=request.user).prefetch_related('skills')
    
    # Get notification counts for each search
    for search in saved_searches_list:
        search.unread_count = SearchNotification.objects.filter(
            saved_search=search,
            is_read=False
        ).count()
    
    return render(request, 'user_profiles/saved_searches.html', {
        'saved_searches': saved_searches_list
    })

@login_required
def delete_saved_search(request, search_id):
    """
    Delete a saved candidate search.
    """
    # Only recruiters can delete searches
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can delete saved searches.')
        return redirect('homepage.index')
    
    saved_search = get_object_or_404(SavedCandidateSearch, id=search_id, recruiter=request.user)
    
    if request.method == 'POST':
        search_name = saved_search.name
        saved_search.delete()
        messages.success(request, f'Search "{search_name}" deleted successfully.')
        return redirect('user_profiles.saved_searches')
    
    return render(request, 'user_profiles/delete_saved_search.html', {
        'saved_search': saved_search
    })

@login_required
def search_notifications(request):
    """
    View all notifications for new candidate matches.
    """
    # Only recruiters can view notifications
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can view search notifications.')
        return redirect('homepage.index')
    
    # Get all notifications for this recruiter's saved searches
    notifications = SearchNotification.objects.filter(
        saved_search__recruiter=request.user
    ).select_related('saved_search', 'candidate', 'candidate__user').order_by('-created_at')
    
    unread_count = notifications.filter(is_read=False).count()
    
    return render(request, 'user_profiles/search_notifications.html', {
        'notifications': notifications,
        'unread_count': unread_count
    })

@login_required
def mark_notification_read(request, notification_id):
    """
    Mark a notification as read.
    """
    # Only recruiters can mark notifications as read
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        return JsonResponse({'success': False, 'error': 'Unauthorized'})
    
    notification = get_object_or_404(
        SearchNotification,
        id=notification_id,
        saved_search__recruiter=request.user
    )
    
    if request.method == 'POST':
        notification.is_read = True
        notification.save()
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False, 'error': 'Invalid request method'})

@login_required
def check_new_matches(request, search_id=None):
    """
    Check for new matches in saved searches. Can be called for a specific search or all active searches.
    """
    # Only recruiters can check for matches
    if not hasattr(request.user, 'userprofile') or request.user.userprofile.user_type != 'recruiter':
        messages.error(request, 'Only recruiters can check for new matches.')
        return redirect('homepage.index')
    
    if search_id:
        searches = SavedCandidateSearch.objects.filter(id=search_id, recruiter=request.user, is_active=True)
    else:
        searches = SavedCandidateSearch.objects.filter(recruiter=request.user, is_active=True)
    
    new_matches_count = 0
    
    for saved_search in searches:
        matches = _find_matches_for_search(saved_search)
        for candidate in matches:
            # Check if notification already exists
            notification, created = SearchNotification.objects.get_or_create(
                saved_search=saved_search,
                candidate=candidate,
                defaults={'is_read': False}
            )
            if created:
                new_matches_count += 1
        
        # Update last_checked_at
        saved_search.last_checked_at = timezone.now()
        saved_search.save()
    
    if search_id:
        messages.success(request, f'Found {new_matches_count} new match(es)!')
        return redirect('user_profiles.saved_searches')
    else:
        messages.success(request, f'Checked all searches. Found {new_matches_count} new match(es)!')
        return redirect('user_profiles.search_notifications')

def _find_matches_for_search(saved_search):
    """
    Helper function to find candidate matches for a saved search.
    Returns a queryset of JobSeekerProfile objects that match the search criteria.
    """
    profiles = JobSeekerProfile.objects.filter(user__userprofile__user_type='job_seeker')
    
    # Filter by skills
    if saved_search.skills.exists():
        profiles = profiles.filter(skills__in=saved_search.skills.all()).distinct()
    
    # Filter by location (search in email, preferred_location, or work experience location)
    if saved_search.location:
        profiles = profiles.filter(
            Q(email__icontains=saved_search.location) |
            Q(preferred_location__icontains=saved_search.location) |
            Q(experience__location__icontains=saved_search.location)
        ).distinct()
    
    # Filter by project keywords
    if saved_search.project_keywords:
        profiles = profiles.filter(
            Q(experience__description__icontains=saved_search.project_keywords) |
            Q(experience__title__icontains=saved_search.project_keywords)
        ).distinct()
    
    # Exclude candidates that already have notifications for this search
    existing_notifications = SearchNotification.objects.filter(
        saved_search=saved_search
    ).values_list('candidate_id', flat=True)
    
    profiles = profiles.exclude(id__in=existing_notifications)
    
    return profiles
