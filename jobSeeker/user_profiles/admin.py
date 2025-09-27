from django.contrib import admin
from .models import JobSeekerProfile, WorkExperience, Education, Skill, Link

admin.site.register(JobSeekerProfile)
admin.site.register(WorkExperience)
admin.site.register(Education)
admin.site.register(Skill)
admin.site.register(Link)
