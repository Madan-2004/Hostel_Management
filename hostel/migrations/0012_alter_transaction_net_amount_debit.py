# Generated by Django 5.0.3 on 2024-03-29 19:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0011_transaction_room_institute_use'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transaction',
            name='net_amount_debit',
            field=models.DecimalField(decimal_places=2, max_digits=10),
        ),
    ]
