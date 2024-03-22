from django.db import models
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Room(models.Model):
    Room_Choices = {
        "1": "Basic",
        "2": "Premium"
    }

    room_no = models.CharField(max_length = 4, unique = True)
    floor = models.IntegerField(default = 0, validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ])
    category = models.CharField(max_length = 1, default = "1")
    capacity = models.IntegerField(default = 1, validators=[MinValueValidator(0)])

    def __str__(self):
        return f'Room number - {self.room_no}.'
    
class Booking(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    phone_number = models.CharField(max_length=15, default=9876543210)
    email = models.EmailField(default='all@iiti.ac.in')
    room = models.ForeignKey(Room, on_delete = models.CASCADE)

    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f'{self.user} has booked {self.room}.'
    


