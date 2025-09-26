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
        
        # Sample job data
        sample_jobs = [
            {
                'title': 'Senior Python Developer',
                'company': 'TechCorp Inc.',
                'location': 'San Francisco, CA',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'work_location': 'hybrid',
                'salary_min': Decimal('120000.00'),
                'salary_max': Decimal('160000.00'),
                'visa_sponsorship': True,
                'description': 'We are looking for a senior Python developer to join our growing team. You will work on building scalable web applications using Django and modern Python frameworks.',
                'requirements': '5+ years of Python experience, Django framework knowledge, experience with REST APIs, database design skills.',
                'skills': ['Python', 'Django', 'REST API', 'PostgreSQL', 'AWS']
            },
            {
                'title': 'Frontend React Developer',
                'company': 'StartupXYZ',
                'location': 'New York, NY',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'work_location': 'remote',
                'salary_min': Decimal('80000.00'),
                'salary_max': Decimal('110000.00'),
                'visa_sponsorship': False,
                'description': 'Join our dynamic frontend team to build amazing user experiences with React and modern JavaScript.',
                'requirements': '3+ years React experience, JavaScript ES6+, HTML/CSS, responsive design.',
                'skills': ['React', 'JavaScript', 'HTML', 'CSS', 'Bootstrap']
            },
            {
                'title': 'Data Scientist',
                'company': 'DataAnalytics Co.',
                'location': 'Seattle, WA',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'work_location': 'on_site',
                'salary_min': Decimal('130000.00'),
                'salary_max': Decimal('180000.00'),
                'visa_sponsorship': True,
                'description': 'Lead data science initiatives and build machine learning models to drive business insights.',
                'requirements': 'PhD in Data Science or related field, 5+ years ML experience, Python/R, statistical analysis.',
                'skills': ['Python', 'Machine Learning', 'Data Science', 'SQL', 'AWS']
            },
            {
                'title': 'DevOps Engineer',
                'company': 'CloudTech Solutions',
                'location': 'Austin, TX',
                'job_type': 'full_time',
                'experience_level': 'mid',
                'work_location': 'hybrid',
                'salary_min': Decimal('95000.00'),
                'salary_max': Decimal('125000.00'),
                'visa_sponsorship': True,
                'description': 'Manage cloud infrastructure and implement CI/CD pipelines for our development teams.',
                'requirements': '3+ years DevOps experience, AWS/Azure, Docker, Kubernetes, CI/CD tools.',
                'skills': ['AWS', 'Docker', 'Kubernetes', 'CI/CD', 'Linux', 'Jenkins']
            },
            {
                'title': 'Full Stack Developer',
                'company': 'WebSolutions Ltd.',
                'location': 'Chicago, IL',
                'job_type': 'contract',
                'experience_level': 'mid',
                'work_location': 'remote',
                'salary_min': Decimal('70000.00'),
                'salary_max': Decimal('90000.00'),
                'visa_sponsorship': False,
                'description': 'Work on both frontend and backend development for our client projects.',
                'requirements': 'Full stack development experience, Node.js, React, database design.',
                'skills': ['JavaScript', 'Node.js', 'React', 'SQL', 'MongoDB']
            },
            {
                'title': 'Junior Software Engineer',
                'company': 'EntryLevel Tech',
                'location': 'Denver, CO',
                'job_type': 'full_time',
                'experience_level': 'entry',
                'work_location': 'on_site',
                'salary_min': Decimal('55000.00'),
                'salary_max': Decimal('70000.00'),
                'visa_sponsorship': False,
                'description': 'Great opportunity for recent graduates to start their tech career with mentorship and growth opportunities.',
                'requirements': 'Computer Science degree, programming fundamentals, eagerness to learn.',
                'skills': ['Python', 'JavaScript', 'Git', 'Problem Solving', 'Teamwork']
            }
        ]
        
        # Create sample jobs
        for job_data in sample_jobs:
            skills_list = job_data.pop('skills')
            job, created = Job.objects.get_or_create(
                title=job_data['title'],
                company=job_data['company'],
                defaults={
                    **job_data,
                    'posted_by': recruiter
                }
            )
            
            if created:
                # Add skills to the job
                for skill_name in skills_list:
                    try:
                        skill = Skill.objects.get(name=skill_name)
                        job.skills_required.add(skill)
                    except Skill.DoesNotExist:
                        pass
                
                self.stdout.write(f'Created job: {job.title} at {job.company}')
            else:
                self.stdout.write(f'Job already exists: {job.title} at {job.company}')
        
        self.stdout.write(
            self.style.SUCCESS('Successfully populated database with sample data!')
        )
