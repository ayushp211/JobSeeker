# Generated manually to remove old status field

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job_postings', '0008_migrate_status_data'),
    ]

    operations = [
        # Remove the old status_old field
        migrations.RemoveField(
            model_name='jobapplication',
            name='status_old',
        ),
    ]

