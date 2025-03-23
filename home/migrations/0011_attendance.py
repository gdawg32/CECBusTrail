# Generated by Django 4.2.4 on 2025-03-23 13:09

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0010_student_admission_number'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendance',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=django.utils.timezone.now)),
                ('time', models.TimeField(auto_now_add=True)),
                ('route', models.CharField(choices=[('to', 'To College'), ('from', 'From College')], max_length=10)),
                ('student', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attendances', to='home.student')),
            ],
            options={
                'unique_together': {('student', 'date', 'route')},
            },
        ),
    ]
