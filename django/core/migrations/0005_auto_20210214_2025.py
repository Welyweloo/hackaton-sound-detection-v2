# Generated by Django 3.0.8 on 2021-02-14 20:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_detection_fake_positive'),
    ]

    operations = [
        migrations.RenameField(
            model_name='detection',
            old_name='fake_positive',
            new_name='false_positive',
        ),
    ]
