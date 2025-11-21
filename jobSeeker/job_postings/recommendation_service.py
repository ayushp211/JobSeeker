# US#16: Candidate Recommendation Service
# This module generates candidate recommendations for job postings based on job attributes
# such as skills, experience level, and other matching criteria.

from datetime import date
from django.db.models import Q, Count
from user_profiles.models import JobSeekerProfile, WorkExperience
from .models import Job, JobApplication


def get_candidate_recommendations_for_job(job, limit=10):
    """
    US#16: Generate candidate recommendations for a given job posting.
    
    This function matches job seekers to a job based on:
    - Skills overlap (primary matching factor)
    - Experience level compatibility
    - Excludes candidates who have already applied
    
    Args:
        job: Job instance to generate recommendations for
        limit: Maximum number of recommendations to return (default: 10)
    
    Returns:
        List of dictionaries containing:
        - 'profile': JobSeekerProfile instance
        - 'match_score': Float score (0-100) indicating match quality
        - 'matching_skills': QuerySet of matching skills
        - 'skill_match_count': Number of matching skills
        - 'total_required_skills': Total skills required by the job
    """
    # Get all job seekers (exclude recruiters)
    from user_accounts.models import UserProfile
    job_seeker_users = UserProfile.objects.filter(user_type='job_seeker').values_list('user_id', flat=True)
    
    # Get profiles of job seekers
    profiles = JobSeekerProfile.objects.filter(user_id__in=job_seeker_users)
    
    # Exclude candidates who have already applied to this job
    applied_user_ids = JobApplication.objects.filter(job=job).values_list('applicant_id', flat=True)
    profiles = profiles.exclude(user_id__in=applied_user_ids)
    
    # Get required skills for the job
    required_skills_qs = job.skills_required.all()
    
    if not required_skills_qs.exists():
        # If no skills required, return profiles sorted by profile completeness
        # (profiles with more information are ranked higher)
        profiles_with_scores = []
        for profile in profiles[:limit]:
            score = _calculate_profile_completeness_score(profile)
            profiles_with_scores.append({
                'profile': profile,
                'match_score': score,
                'matching_skills': [],
                'skill_match_count': 0,
                'total_required_skills': 0,
            })
        return sorted(profiles_with_scores, key=lambda x: x['match_score'], reverse=True)
    
    # Normalize required skills into a Python list and lowercase name set for robust matching
    required_skills = list(required_skills_qs)
    required_skill_names = {s.name.strip().lower() for s in required_skills}
    
    # Calculate match scores for each profile
    profiles_with_scores = []
    for profile in profiles:
        # Get profile skills and compute matching skills in Python (case-insensitive by name)
        profile_skills = list(profile.skills.all())
        matching_skills = [
            skill for skill in profile_skills
            if skill.name and skill.name.strip().lower() in required_skill_names
        ]
        skill_match_count = len(matching_skills)
        total_required_skills = len(required_skills)
        
        # Calculate skill match percentage (primary factor, 70% weight)
        skill_match_percentage = (skill_match_count / total_required_skills * 100) if total_required_skills > 0 else 0
        
        # Calculate experience level match (secondary factor, 20% weight)
        experience_score = _calculate_experience_match(job, profile)
        
        # Calculate profile completeness (tertiary factor, 10% weight)
        completeness_score = _calculate_profile_completeness_score(profile)
        
        # Calculate overall match score
        match_score = (
            skill_match_percentage * 0.7 +
            experience_score * 0.2 +
            completeness_score * 0.1
        )
        
        # Only include profiles with at least one matching skill
        if skill_match_count > 0:
            profiles_with_scores.append({
                'profile': profile,
                'match_score': match_score,
                'matching_skills': matching_skills,
                'skill_match_count': skill_match_count,
                'total_required_skills': total_required_skills,
            })
    
    # Sort by match score (descending) and return top results
    profiles_with_scores.sort(key=lambda x: x['match_score'], reverse=True)
    return profiles_with_scores[:limit]


def _calculate_experience_match(job, profile):
    """
    US#16: Calculate how well a candidate's experience level matches the job requirement.
    
    Returns a score from 0-100 based on experience level compatibility.
    """
    # Map job experience levels to numeric values for comparison
    experience_levels = {
        'entry': 1,
        'mid': 2,
        'senior': 3,
        'executive': 4,
    }
    
    job_level = experience_levels.get(job.experience_level, 2)
    
    # Get candidate's work experience
    work_experiences = profile.experience.all()
    
    if not work_experiences.exists():
        # No experience - only suitable for entry level
        if job.experience_level == 'entry':
            return 80
        return 20
    
    # Calculate years of experience from work history
    total_years = 0
    for exp in work_experiences:
        if exp.end_date:
            years = (exp.end_date - exp.start_date).days / 365.25
        else:
            # Current position
            years = (date.today() - exp.start_date).days / 365.25
        total_years += years
    
    # Map years of experience to levels
    if total_years < 2:
        candidate_level = 1  # Entry
    elif total_years < 5:
        candidate_level = 2  # Mid
    elif total_years < 10:
        candidate_level = 3  # Senior
    else:
        candidate_level = 4  # Executive
    
    # Calculate match score
    level_diff = abs(job_level - candidate_level)
    if level_diff == 0:
        return 100
    elif level_diff == 1:
        return 75
    elif level_diff == 2:
        return 50
    else:
        return 25


def _calculate_profile_completeness_score(profile):
    """
    US#16: Calculate profile completeness score based on filled fields.
    
    Returns a score from 0-100 indicating how complete the profile is.
    """
    score = 0
    max_score = 100
    
    # Check each profile component
    if profile.first_name and profile.last_name:
        score += 10
    if profile.email:
        score += 10
    if profile.headline:
        score += 10
    if profile.skills.exists():
        score += 20
    if profile.experience.exists():
        score += 25
    if profile.education.exists():
        score += 15
    if profile.links.exists():
        score += 10
    
    return min(score, max_score)

