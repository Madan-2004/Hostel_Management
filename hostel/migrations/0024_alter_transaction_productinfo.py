# Generated by Django 5.0.3 on 2024-04-12 10:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0023_reservation_payment_method_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='productinfo',
            field=models.CharField(default='IIT INDORE', max_length=255),
        ),
    ]
