# Generated by Django 5.1.4 on 2024-12-26 18:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0031_participant_user_userprofile_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='participant',
            name='email',
            field=models.EmailField(max_length=254),
        ),
        migrations.AlterField(
            model_name='participant',
            name='phone',
            field=models.CharField(max_length=20),
        ),
        migrations.AlterUniqueTogether(
            name='participant',
            unique_together={('phone', 'event')},
        ),
    ]
