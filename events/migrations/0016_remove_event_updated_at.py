# Generated by Django 4.1.1 on 2022-11-30 19:47

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('events', '0015_registeredevent'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='updated_at',
        ),
    ]