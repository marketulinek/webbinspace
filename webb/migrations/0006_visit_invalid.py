# Generated by Django 4.1 on 2022-10-22 18:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webb', '0005_alter_visit_duration'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='invalid',
            field=models.BooleanField(default=False),
        ),
    ]
