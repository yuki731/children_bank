# Generated by Django 4.2 on 2024-07-27 16:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('children_bank_app', '0005_alter_jobcard_job_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='jobcard',
            name='job_image',
            field=models.ImageField(blank=True, null=True, upload_to='job_pictures/'),
        ),
    ]
