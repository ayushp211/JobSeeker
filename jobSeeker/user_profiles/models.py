from django.db import models
from django.contrib.auth.models import User

class Skill(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseekerprofile')
    headline = models.CharField(max_length=255, blank=True, null=True)
    email = models.CharField(max_length=255, blank=True, null=True)
    skills = models.ManyToManyField(Skill, blank=True)
    
    def __str__(self):
        return f"Job Seeker Profile for {self.user.username}"

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

