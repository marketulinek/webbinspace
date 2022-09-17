# Generated by Django 4.1 on 2022-09-08 19:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webb', '0002_alter_category_name_alter_report_package_number_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='visit',
            name='mode',
        ),
        migrations.AlterField(
            model_name='visit',
            name='instrument',
            field=models.CharField(choices=[('0', ''), ('1', 'NIRCam'), ('2', 'NIRSpec'), ('3', 'MIRI'), ('4', 'NIRISS')], default=0, max_length=1),
        ),
    ]