# Generated by Django 4.2.4 on 2025-03-11 12:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0008_studentapplication_semester'),
    ]

    operations = [
        migrations.AddField(
            model_name='bus',
            name='tracking_enabled',
            field=models.BooleanField(default=False),
        ),
    ]
