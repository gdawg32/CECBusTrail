# Generated by Django 4.2.4 on 2025-03-10 17:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0006_student_bus_stop'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='semester',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
