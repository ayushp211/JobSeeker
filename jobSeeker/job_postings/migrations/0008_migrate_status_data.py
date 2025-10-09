# Generated manually to migrate status data from old CharField to new ForeignKey

from django.db import migrations


def migrate_status_data(apps, schema_editor):
    """Convert old status string values to new ApplicationStatus ForeignKeys"""
    ApplicationStatus = apps.get_model('job_postings', 'ApplicationStatus')
    JobApplication = apps.get_model('job_postings', 'JobApplication')
    
    # Mapping of old status values to new status names
    status_mapping = {
        'applied': 'Applied',
        'review': 'Screening',
        'interview': 'Phone Interview',
        'offer': 'Offer',
        'closed': 'Rejected',
    }
    
    # Get or create status objects
    status_objects = {}
    for old_value, new_name in status_mapping.items():
        status_obj, created = ApplicationStatus.objects.get_or_create(
            name=new_name,
            defaults={'order': 0, 'color': '#007bff'}
        )
        status_objects[old_value] = status_obj
    
    # Update all JobApplications
    for application in JobApplication.objects.all():
        if application.status_old and application.status_old in status_objects:
            application.status = status_objects[application.status_old]
            application.save(update_fields=['status'])


def reverse_migrate_status_data(apps, schema_editor):
    """Reverse migration - convert ForeignKey back to CharField values"""
    JobApplication = apps.get_model('job_postings', 'JobApplication')
    
    # Reverse mapping
    reverse_mapping = {
        'Applied': 'applied',
        'Screening': 'review',
        'Phone Interview': 'interview',
        'Offer': 'offer',
        'Rejected': 'closed',
    }
    
    for application in JobApplication.objects.all():
        if application.status:
            status_name = application.status.name
            if status_name in reverse_mapping:
                application.status_old = reverse_mapping[status_name]
                application.save(update_fields=['status_old'])


class Migration(migrations.Migration):

    dependencies = [
        ('job_postings', '0007_add_new_status_field'),
    ]

    operations = [
        migrations.RunPython(migrate_status_data, reverse_migrate_status_data),
    ]

