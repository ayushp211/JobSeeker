from django.core.management.base import BaseCommand
from django.utils import timezone
from user_profiles.models import SavedCandidateSearch, SearchNotification, JobSeekerProfile
from django.db.models import Q

class Command(BaseCommand):
    help = 'Check all active saved candidate searches for new matches and create notifications'

    def handle(self, *args, **options):
        active_searches = SavedCandidateSearch.objects.filter(is_active=True)
        total_new_matches = 0
        
        for saved_search in active_searches:
            new_matches = self.find_new_matches(saved_search)
            
            for candidate in new_matches:
                notification, created = SearchNotification.objects.get_or_create(
                    saved_search=saved_search,
                    candidate=candidate,
                    defaults={'is_read': False}
                )
                if created:
                    total_new_matches += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'New match: {candidate.user.username} for search "{saved_search.name}"'
                        )
                    )
            
            # Update last_checked_at
            saved_search.last_checked_at = timezone.now()
            saved_search.save()
        
        if total_new_matches > 0:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nFound {total_new_matches} new match(es) across {active_searches.count()} active search(es).'
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f'\nNo new matches found. Checked {active_searches.count()} active search(es).'
                )
            )
    
    def find_new_matches(self, saved_search):
        """
        Find candidate matches for a saved search that don't already have notifications.
        """
        profiles = JobSeekerProfile.objects.filter(user__userprofile__user_type='job_seeker')
        
        # Filter by skills
        if saved_search.skills.exists():
            profiles = profiles.filter(skills__in=saved_search.skills.all()).distinct()
        
        # Filter by location (search in email, preferred_location, or work experience location)
        if saved_search.location:
            profiles = profiles.filter(
                Q(email__icontains=saved_search.location) |
                Q(preferred_location__icontains=saved_search.location) |
                Q(experience__location__icontains=saved_search.location)
            ).distinct()
        
        # Filter by project keywords
        if saved_search.project_keywords:
            profiles = profiles.filter(
                Q(experience__description__icontains=saved_search.project_keywords) |
                Q(experience__title__icontains=saved_search.project_keywords)
            ).distinct()
        
        # Exclude candidates that already have notifications for this search
        existing_notifications = SearchNotification.objects.filter(
            saved_search=saved_search
        ).values_list('candidate_id', flat=True)
        
        profiles = profiles.exclude(id__in=existing_notifications)
        
        return profiles

