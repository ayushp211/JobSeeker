# Generated manually to populate default pipeline statuses

from django.db import migrations


def create_default_statuses(apps, schema_editor):
    """Create default pipeline statuses"""
    ApplicationStatus = apps.get_model('job_postings', 'ApplicationStatus')
    
    default_statuses = [
        {'name': 'Applied', 'order': 1, 'color': '#007bff'},  # Blue
        {'name': 'Screening', 'order': 2, 'color': '#6f42c1'},  # Purple
        {'name': 'Phone Interview', 'order': 3, 'color': '#fd7e14'},  # Orange
        {'name': 'Technical Interview', 'order': 4, 'color': '#ffc107'},  # Yellow
        {'name': 'Final Interview', 'order': 5, 'color': '#0dcaf0'},  # Cyan
        {'name': 'Offer', 'order': 6, 'color': '#28a745'},  # Green
        {'name': 'Rejected', 'order': 7, 'color': '#dc3545'},  # Red
        {'name': 'Withdrawn', 'order': 8, 'color': '#6c757d'},  # Gray
    ]
    
    for status_data in default_statuses:
        ApplicationStatus.objects.get_or_create(**status_data)


def remove_default_statuses(apps, schema_editor):
    """Remove default pipeline statuses"""
    ApplicationStatus = apps.get_model('job_postings', 'ApplicationStatus')
    
    default_status_names = [
        'Applied', 'Screening', 'Phone Interview', 'Technical Interview',
        'Final Interview', 'Offer', 'Rejected', 'Withdrawn'
    ]
    
    ApplicationStatus.objects.filter(name__in=default_status_names).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('job_postings', '0005_applicationstatus_and_notes'),
    ]

    operations = [
        migrations.RunPython(create_default_statuses, remove_default_statuses),
    ]

