# Generated by Django 5.1.4 on 2025-01-01 05:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('registration', '0043_paymentstatus_trxid'),
    ]

    operations = [
        migrations.AddField(
            model_name='paymentstatus',
            name='invoice',
            field=models.FileField(blank=True, null=True, upload_to='invoices/'),
        ),
    ]
