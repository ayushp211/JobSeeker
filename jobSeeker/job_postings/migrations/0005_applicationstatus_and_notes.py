# Generated manually to add ApplicationStatus model and notes field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job_postings', '0004_jobapplication_status_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True)),
                ('order', models.PositiveIntegerField(default=0, help_text="Order in which this status appears in the pipeline")),
                ('color', models.CharField(default='#007bff', max_length=7, help_text="Hex color code for the status")),
            ],
            options={
                'ordering': ['order'],
                'verbose_name_plural': 'Application Statuses',
            },
        ),
        migrations.AddField(
            model_name='jobapplication',
            name='notes',
            field=models.TextField(blank=True, help_text='Internal notes for recruiters'),
        ),
    ]

