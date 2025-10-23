from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
from user_profiles.models import Skill
import urllib.request
import urllib.parse
import json

# Create your models here.

class ApplicationStatus(models.Model):
    """
    Represents a status in the application pipeline (e.g., Applied, Interview, Offer).
    Recruiters can customize these statuses to match their hiring process.
    """
    name = models.CharField(max_length=50, unique=True)
    order = models.PositiveIntegerField(default=0, help_text="Order in which this status appears in the pipeline")
    color = models.CharField(max_length=7, default='#007bff', help_text="Hex color code for the status")
    
    class Meta:
        ordering = ['order']
        verbose_name_plural = 'Application Statuses'
    
    def __str__(self):
        return self.name

class Job(models.Model):
    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    ]
    
    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
    ]
    
    WORK_LOCATION_CHOICES = [
        ('remote', 'Remote'),
        ('on_site', 'On-site'),
        ('hybrid', 'Hybrid'),
    ]
    
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=500, help_text="Job location (will be used for map pinning)")
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Latitude for map pin (auto-generated from location)")
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, help_text="Longitude for map pin (auto-generated from location)")
    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, default='full_time')
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, default='entry')
    work_location = models.CharField(max_length=20, choices=WORK_LOCATION_CHOICES, default='on_site')
    salary_min = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    visa_sponsorship = models.BooleanField(default=False)
    skills_required = models.ManyToManyField(Skill, blank=True, related_name='jobs_requiring_skill')
    description = models.TextField()
    requirements = models.TextField()
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_postings')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} at {self.company}"
    
    def get_absolute_url(self):
        return reverse('job_postings.show', kwargs={'id': self.pk})
    
    def geocode_location(self):
        """Geocode the location field to get latitude and longitude coordinates"""
        if not self.location:
            return False
        
        try:
            # Use OpenStreetMap Nominatim API for geocoding
            encoded_location = urllib.parse.quote(self.location)
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
    
    def save(self, *args, **kwargs):
        # Auto-geocode location if it's provided but coordinates aren't
        if self.location and (not self.latitude or not self.longitude):
            self.geocode_location()
        super().save(*args, **kwargs)

class JobApplication(models.Model):
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    cover_note = models.TextField(help_text="Personalize your application with a tailored note")
    status = models.ForeignKey(ApplicationStatus, on_delete=models.CASCADE, related_name='applications', null=True, blank=True)
    notes = models.TextField(blank=True, help_text="Internal notes for recruiters")
    applied_at = models.DateTimeField(auto_now_add=True)
    status_updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        # Auto-assign "Applied" status if no status is set
        if not self.status_id:
            try:
                applied_status = ApplicationStatus.objects.get(name='Applied')
                self.status = applied_status
            except ApplicationStatus.DoesNotExist:
                pass
        super().save(*args, **kwargs)
    
    class Meta:
        unique_together = ('job', 'applicant')  # Prevent duplicate applications
        ordering = ['-applied_at']
    
    def __str__(self):
        return f"{self.applicant.username} applied to {self.job.title} at {self.job.company}"
    
    def get_status_display_class(self):
        """Return Bootstrap CSS class for status badge"""
        if not self.status:
            return 'bg-secondary'
        # You can customize colors per status or use the status.color field
        return 'bg-primary'
