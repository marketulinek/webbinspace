# Generated by Django 4.1 on 2022-10-22 18:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webb', '0007_remove_visit_invalid'),
    ]

    operations = [
        migrations.AddField(
            model_name='visit',
            name='valid',
            field=models.BooleanField(default=True),
        ),
    ]