# Generated by Django 4.2.4 on 2025-03-10 17:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0005_studentapplication_registered_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='student',
            name='bus_stop',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='home.busstop'),
        ),
    ]
