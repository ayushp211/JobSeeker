# Generated manually to add new status field as ForeignKey

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_postings', '0006_populate_default_statuses'),
    ]

    operations = [
        # Rename old status field to status_old temporarily
        migrations.RenameField(
            model_name='jobapplication',
            old_name='status',
            new_name='status_old',
        ),
        # Add new status field as ForeignKey
        migrations.AddField(
            model_name='jobapplication',
            name='status',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='applications',
                to='job_postings.applicationstatus'
            ),
        ),
    ]

