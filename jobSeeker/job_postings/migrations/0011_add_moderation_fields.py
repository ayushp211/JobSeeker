# Migration to add moderation fields to Job model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('job_postings', '0010_set_fixed_statuses'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='is_flagged',
            field=models.BooleanField(default=False, help_text='Flagged by admin for review'),
        ),
        migrations.AddField(
            model_name='job',
            name='flagged_reason',
            field=models.TextField(blank=True, help_text='Reason for flagging'),
        ),
        migrations.AddField(
            model_name='job',
            name='flagged_at',
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='flagged_by',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='flagged_jobs', to=settings.AUTH_USER_MODEL),
        ),
    ]

