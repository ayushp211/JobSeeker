# Migration to set up simple fixed statuses

from django.db import migrations


def create_fixed_statuses(apps, schema_editor):
    """Create only the 5 fixed statuses we need"""
    ApplicationStatus = apps.get_model('job_postings', 'ApplicationStatus')
    
    # Delete all existing statuses
    ApplicationStatus.objects.all().delete()
    
    # Create only the fixed statuses
    fixed_statuses = [
        {'name': 'Applied', 'order': 1, 'color': '#007bff'},
        {'name': 'Review', 'order': 2, 'color': '#ffc107'},
        {'name': 'Interview', 'order': 3, 'color': '#17a2b8'},
        {'name': 'Offer', 'order': 4, 'color': '#28a745'},
        {'name': 'Closed', 'order': 5, 'color': '#6c757d'},
    ]
    
    for status_data in fixed_statuses:
        ApplicationStatus.objects.create(**status_data)


class Migration(migrations.Migration):

    dependencies = [
        ('job_postings', '0009_remove_old_status_field'),
    ]

    operations = [
        migrations.RunPython(create_fixed_statuses, migrations.RunPython.noop),
    ]

