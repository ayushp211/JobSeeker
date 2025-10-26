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
        
        # Create sample jobs with locations
        sample_jobs = [
            {
                'title': 'Senior Software Engineer',
                'company': 'Tech Corp',
                'location': 'San Francisco, CA',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'work_location': 'hybrid',
                'salary_min': Decimal('120000'),
                'salary_max': Decimal('180000'),
                'description': 'We are looking for a senior software engineer to join our innovative team.',
                'requirements': '5+ years of experience in software development, Python, Django, PostgreSQL',
                'is_active': True,
            },
            {
                'title': 'Full Stack Developer',
                'company': 'StartupXYZ',
                'location': 'Atlanta, GA',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'work_location': 'remote',
                'salary_min': Decimal('90000'),
                'salary_max': Decimal('120000'),
                'description': 'Join our dynamic team as a full stack developer working on cutting-edge web applications.',
                'requirements': 'JavaScript, React, Node.js, 3+ years experience',
                'is_active': True,
            },
            {
                'title': 'Data Scientist',
                'company': 'DataTech Inc',
                'location': 'New York, NY',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'work_location': 'on_site',
                'salary_min': Decimal('100000'),
                'salary_max': Decimal('150000'),
                'description': 'Seeking a talented data scientist to work on machine learning projects.',
                'requirements': 'Python, Machine Learning, SQL, Statistics background',
                'is_active': True,
            },
            {
                'title': 'Frontend Developer',
                'company': 'WebApps Co',
                'location': 'Seattle, WA',
                'job_type': 'full_time',
                'experience_level': 'entry',
                'work_location': 'hybrid',
                'salary_min': Decimal('70000'),
                'salary_max': Decimal('95000'),
                'description': 'We are seeking a creative frontend developer to build beautiful user interfaces.',
                'requirements': 'HTML, CSS, JavaScript, React, portfolio required',
                'is_active': True,
            },
            {
                'title': 'DevOps Engineer',
                'company': 'Cloud Systems',
                'location': 'Austin, TX',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'work_location': 'remote',
                'salary_min': Decimal('110000'),
                'salary_max': Decimal('160000'),
                'description': 'Help us build and maintain scalable cloud infrastructure.',
                'requirements': 'AWS, Docker, Kubernetes, CI/CD, 4+ years experience',
                'is_active': True,
            },
        ]
        
        for job_data in sample_jobs:
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                location=job_data['location'],
                defaults={
                    **job_data,
                    'posted_by': recruiter,
                }
            )
            
            # Try to geocode if coordinates don't exist
            if created and (not job.latitude or not job.longitude):
                job.geocode_location()
                job.save()
                
                # Assign some skills to the job
                available_skills = Skill.objects.all()[:5]
                job.skills_required.set(available_skills)
            
            if created:
                self.stdout.write(f'Created job: {job.title} at {job.company}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with skills, recruiter user, and sample jobs!')
        )
