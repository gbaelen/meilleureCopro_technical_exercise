# Generated by Django 5.2.1 on 2025-05-08 15:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='realestatelisting',
            name='surface',
            field=models.JSONField(blank=True, null=True),
        ),
    ]
