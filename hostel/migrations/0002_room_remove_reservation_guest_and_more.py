# Generated by Django 4.2.10 on 2024-03-14 11:12

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('hostel', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('room_no', models.CharField(max_length=4, unique=True)),
                ('floor', models.IntegerField(default=0, max_length=1)),
                ('category', models.CharField(default='1', max_length=1)),
                ('capacity', models.IntegerField(default=1, max_length=1)),
                ('is_occupied', models.BooleanField(default=False)),
            ],
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='guest',
        ),
        migrations.RemoveField(
            model_name='reservation',
            name='room',
        ),
        migrations.RemoveField(
            model_name='rooms',
            name='roomnumber',
        ),
        migrations.DeleteModel(
            name='Hotels',
        ),
        migrations.DeleteModel(
            name='Reservation',
        ),
        migrations.DeleteModel(
            name='Rooms',
        ),
    ]
