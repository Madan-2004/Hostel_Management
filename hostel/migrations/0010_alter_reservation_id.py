# Generated by Django 5.0.3 on 2024-03-29 13:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0009_alter_reservation_room_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reservation',
            name='id',
            field=models.AutoField(primary_key=True, serialize=False),
        ),
    ]
