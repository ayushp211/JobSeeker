from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from job_postings.models import Job
from user_profiles.models import Skill
from user_accounts.models import UserProfile
from decimal import Decimal

class Command(BaseCommand):
    help = 'Populate database with sample jobs and skills'

    def handle(self, *args, **options):
        # Create sample skills
        skills_data = [
            'Python', 'Django', 'JavaScript', 'React', 'Node.js', 'SQL', 'PostgreSQL',
            'MongoDB', 'AWS', 'Docker', 'Kubernetes', 'Git', 'Linux', 'Machine Learning',
            'Data Science', 'Java', 'Spring Boot', 'Angular', 'Vue.js', 'TypeScript',
            'HTML', 'CSS', 'Bootstrap', 'REST API', 'GraphQL', 'Redis', 'Elasticsearch',
            'Jenkins', 'CI/CD', 'Agile', 'Scrum', 'Project Management', 'Leadership',
            'Communication', 'Problem Solving', 'Teamwork', 'Analytical Skills'
        ]
        
        skills = []
        for skill_name in skills_data:
            skill, created = Skill.objects.get_or_create(name=skill_name)
            skills.append(skill)
            if created:
                self.stdout.write(f'Created skill: {skill_name}')
        
        # Create a sample recruiter user if it doesn't exist
        recruiter, created = User.objects.get_or_create(
            username='recruiter1',
            defaults={
                'email': 'recruiter1@example.com',
                'first_name': 'John',
                'last_name': 'Recruiter'
            }
        )
        if created:
            recruiter.set_password('password123')
            recruiter.save()
            self.stdout.write('Created recruiter user')
        
        # Create user profile for recruiter
        profile, created = UserProfile.objects.get_or_create(
            user=recruiter,
            defaults={'user_type': 'recruiter'}
        )
        if created:
            self.stdout.write('Created recruiter profile')
        
        # No sample jobs - only create skills and recruiter user
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with skills and recruiter user!')
        )
