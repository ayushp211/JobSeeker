from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseekerprofile')
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    headline = models.CharField(max_length=255, blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    
    # Location fields for distance-based job search
    preferred_location = models.CharField(max_length=500, blank=True, null=True, help_text="Your preferred job search location (e.g., 'Atlanta, GA')")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude for your location")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude for your location")
    commute_radius = models.DecimalField(max_digits=5, decimal_places=1, default=25.0, help_text="Preferred commute radius in miles")

    is_headline_public = models.BooleanField(default=True, verbose_name="Make 'About Me' Public")
    is_experience_public = models.BooleanField(default=True, verbose_name="Make Work Experience Public")
    is_education_public = models.BooleanField(default=True, verbose_name="Make Education Public")
    is_skills_public = models.BooleanField(default=True, verbose_name="Make Skills Public")
    is_links_public = models.BooleanField(default=True, verbose_name="Make Links Public")
    
    def __str__(self):
        return f"Job Seeker Profile for {self.user.username}"
    
    def geocode_preferred_location(self):
        """Geocode the preferred_location field to get latitude and longitude coordinates"""
        if not self.preferred_location:
            return False
        
        import urllib.request
        import urllib.parse
        import json
        
        try:
            # Use OpenStreetMap Nominatim API for geocoding
            encoded_location = urllib.parse.quote(self.preferred_location)
            url = f"https://nominatim.openstreetmap.org/search?format=json&q={encoded_location}&limit=1"
            
            with urllib.request.urlopen(url, timeout=10) as response:
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    if data and len(data) > 0:
                        self.latitude = float(data[0]['lat'])
                        self.longitude = float(data[0]['lon'])
                        return True
        except Exception as e:
            print(f"Geocoding error: {e}")
        
        return False

class Education(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='education')
    school = models.CharField(max_length=255)
    degree = models.CharField(max_length=255)
    field_of_study = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.degree} at {self.school}"

class WorkExperience(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='experience')
    company = models.CharField(max_length=255)
    title = models.CharField(max_length=255)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-start_date']

    def __str__(self):
        return f"{self.title} at {self.company}"

class Link(models.Model):
    profile = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='links')
    name = models.CharField(max_length=100, help_text='e.g., "Portfolio", "LinkedIn"')
    url = models.URLField()

    def __str__(self):
        return f"{self.name} ({self.url})"

class SavedCandidateSearch(models.Model):
    """
    Stores saved candidate searches for recruiters.
    """
    recruiter = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_candidate_searches')
    name = models.CharField(max_length=200, help_text='Name for this saved search')
    skills = models.ManyToManyField(Skill, blank=True, related_name='saved_searches')
    location = models.CharField(max_length=255, blank=True, null=True)
    project_keywords = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    last_checked_at = models.DateTimeField(null=True, blank=True, help_text='Last time this search was checked for new matches')
    is_active = models.BooleanField(default=True, help_text='Whether to check for new matches')
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = 'Saved Candidate Searches'
    
    def __str__(self):
        return f"{self.name} - {self.recruiter.username}"
    
    def get_search_url(self):
        """Returns the URL to perform this search"""
        from django.urls import reverse
        from urllib.parse import urlencode
        
        params = {}
        if self.skills.exists():
            params['skills'] = [s.id for s in self.skills.all()]
        if self.location:
            params['location'] = self.location
        if self.project_keywords:
            params['project_keywords'] = self.project_keywords
        
        base_url = reverse('user_profiles.search_candidates')
        if params:
            return f"{base_url}?{urlencode(params, doseq=True)}"
        return base_url

class SearchNotification(models.Model):
    """
    Notifications for new candidate matches in saved searches.
    """
    saved_search = models.ForeignKey(SavedCandidateSearch, on_delete=models.CASCADE, related_name='notifications')
    candidate = models.ForeignKey(JobSeekerProfile, on_delete=models.CASCADE, related_name='search_notifications')
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
        unique_together = ('saved_search', 'candidate')
    
    def __str__(self):
        return f"New match: {self.candidate.user.username} for search '{self.saved_search.name}'"

