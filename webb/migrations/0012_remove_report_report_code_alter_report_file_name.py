# Generated by Django 5.0.8 on 2024-11-08 18:15

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webb', '0011_alter_report_report_code'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='report',
            name='report_code',
        ),
        migrations.AlterField(
            model_name='report',
            name='file_name',
            field=models.CharField(max_length=30, unique=True),
        ),
    ]