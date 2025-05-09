# Generated by Django 5.1.4 on 2024-12-10 15:03

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0010_event_author_event_keywords_event_og_image'),
    ]

    operations = [
        migrations.AddField(
            model_name='event',
            name='description',
            field=models.TextField(blank=True, max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='event',
            name='keywords',
            field=models.CharField(blank=True, help_text='Enter Keywords seperated by comma', max_length=1000, null=True),
        ),
    ]
