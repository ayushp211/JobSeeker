from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from user_accounts.models import UserProfile
from job_postings.models import Job, JobApplication, ApplicationStatus
from messaging.models import Conversation, Message
from datetime import datetime, timedelta
import random

class Command(BaseCommand):
    help = 'Create sample messaging data for testing'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample messaging data...')
        
        # Create sample users if they don't exist
        recruiter, created = User.objects.get_or_create(
            username='recruiter1',
            defaults={
                'email': 'recruiter1@example.com',
                'first_name': 'John',
                'last_name': 'Recruiter',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            recruiter.set_password('password123')
            recruiter.save()
            self.stdout.write(f'Created recruiter: {recruiter.username}')
        
        # Ensure user profile exists and is correct type
        profile, _ = UserProfile.objects.get_or_create(user=recruiter, defaults={'user_type': 'recruiter'})
        if profile.user_type != 'recruiter':
            profile.user_type = 'recruiter'
            profile.save()
        
        job_seeker1, created = User.objects.get_or_create(
            username='jobseeker1',
            defaults={
                'email': 'jobseeker1@example.com',
                'first_name': 'Alice',
                'last_name': 'Developer',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            job_seeker1.set_password('password123')
            job_seeker1.save()
            self.stdout.write(f'Created job seeker: {job_seeker1.username}')
        
        # Ensure user profile exists and is correct type
        profile, _ = UserProfile.objects.get_or_create(user=job_seeker1, defaults={'user_type': 'job_seeker'})
        if profile.user_type != 'job_seeker':
            profile.user_type = 'job_seeker'
            profile.save()
        
        job_seeker2, created = User.objects.get_or_create(
            username='jobseeker2',
            defaults={
                'email': 'jobseeker2@example.com',
                'first_name': 'Bob',
                'last_name': 'Engineer',
                'is_staff': False,
                'is_superuser': False,
            }
        )
        if created:
            job_seeker2.set_password('password123')
            job_seeker2.save()
            self.stdout.write(f'Created job seeker: {job_seeker2.username}')
        
        # Ensure user profile exists and is correct type
        profile, _ = UserProfile.objects.get_or_create(user=job_seeker2, defaults={'user_type': 'job_seeker'})
        if profile.user_type != 'job_seeker':
            profile.user_type = 'job_seeker'
            profile.save()
        
        # Create a sample job
        job, created = Job.objects.get_or_create(
            title='Senior Software Engineer',
            company='Tech Corp',
            defaults={
                'location': 'San Francisco, CA',
                'job_type': 'full_time',
                'experience_level': 'senior',
                'work_location': 'hybrid',
                'salary_min': 120000,
                'salary_max': 180000,
                'description': 'We are looking for a senior software engineer to join our team.',
                'requirements': '5+ years of experience in software development.',
                'posted_by': recruiter,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(f'Created job: {job.title}')
        
        # Create sample applications
        app1, created = JobApplication.objects.get_or_create(
            job=job,
            applicant=job_seeker1,
            defaults={
                'cover_note': 'I am very interested in this position and would love to discuss it further.',
                'notes': 'Strong candidate with relevant experience.',
            }
        )
        if created:
            self.stdout.write(f'Created application for {job_seeker1.username}')
        
        app2, created = JobApplication.objects.get_or_create(
            job=job,
            applicant=job_seeker2,
            defaults={
                'cover_note': 'This role aligns perfectly with my career goals.',
                'notes': 'Excellent technical skills.',
            }
        )
        if created:
            self.stdout.write(f'Created application for {job_seeker2.username}')
        
        # Create sample conversations
        conv1, created = Conversation.objects.get_or_create(
            recruiter=recruiter,
            job_seeker=job_seeker1,
            job=job,
            defaults={
                'subject': 'Interview for Senior Software Engineer Position',
                'application': app1,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(f'Created conversation with {job_seeker1.username}')
            
            # Add sample messages
            Message.objects.create(
                conversation=conv1,
                sender=recruiter,
                content='Hi Alice! Thank you for your application. I would like to schedule an interview with you.',
                is_read=True,
            )
            
            Message.objects.create(
                conversation=conv1,
                sender=job_seeker1,
                content='Hi John! Thank you for reaching out. I would be happy to schedule an interview. What times work best for you?',
                is_read=True,
            )
            
            Message.objects.create(
                conversation=conv1,
                sender=recruiter,
                content='Great! How about next Tuesday at 2 PM? We can do it via video call.',
                is_read=False,
            )
        
        conv2, created = Conversation.objects.get_or_create(
            recruiter=recruiter,
            job_seeker=job_seeker2,
            job=job,
            defaults={
                'subject': 'Follow-up on Software Engineer Application',
                'application': app2,
                'is_active': True,
            }
        )
        if created:
            self.stdout.write(f'Created conversation with {job_seeker2.username}')
            
            # Add sample messages
            Message.objects.create(
                conversation=conv2,
                sender=recruiter,
                content='Hi Bob! I reviewed your application and I\'m impressed with your background.',
                is_read=True,
            )
            
            Message.objects.create(
                conversation=conv2,
                sender=job_seeker2,
                content='Thank you! I\'m very excited about this opportunity.',
                is_read=True,
            )
        
        self.stdout.write(
            self.style.SUCCESS('Successfully created sample messaging data!')
        )
        self.stdout.write('You can now test the messaging functionality with:')
        self.stdout.write('- Recruiter: recruiter1 / password123')
        self.stdout.write('- Job Seeker 1: jobseeker1 / password123')
        self.stdout.write('- Job Seeker 2: jobseeker2 / password123')
