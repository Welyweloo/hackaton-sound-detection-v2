# Generated by Django 3.0.8 on 2021-02-14 14:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patrol',
            name='listening',
            field=models.BooleanField(default=False),
        ),
    ]
