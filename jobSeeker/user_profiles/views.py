from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import JobSeekerProfile
from user_accounts.models import UserProfile 

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

        template_data = {
            'profile': job_seeker_profile,
            'experiences': work_experience,
            'educations': education,
            'skills': skills,
            'links': links,
        }

        return render(request, 'user_profiles/profile.html', {'template_data': template_data})
    
    elif user_profile.user_type == 'recruiter':
        return render(request, 'user_profiles/recruiter_placeholder.html')

