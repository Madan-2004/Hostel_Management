# Generated by Django 5.0.3 on 2024-04-02 20:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0015_remove_transaction_reservation_id_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='reservation',
            name='verified',
            field=models.BooleanField(default=False),
        ),
    ]