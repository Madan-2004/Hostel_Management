from django.db import models
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.

class Room(models.Model):
    ROOM_CHOICES = (
        ("1", "Basic"),
        ("2", "Premium"),
    )

    room_no = models.CharField(max_length = 4, unique = True)
    floor = models.IntegerField(default = 0, validators=[
            MinValueValidator(0),
            MaxValueValidator(5)
        ])
    category = models.CharField(max_length = 1, default = "1", choices = ROOM_CHOICES)
    capacity = models.IntegerField(default = 1, validators=[MinValueValidator(0)])
    rent = models.DecimalField(max_digits=10, decimal_places=2, default=500)
    def __str__(self):
        return f'Room number - {self.room_no}.'
    
class Booking(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete = models.CASCADE)
    phone_number = models.CharField(max_length=15, default=9876543210)
    email = models.EmailField(default='all@iiti.ac.in')
    room = models.ForeignKey(Room, on_delete = models.CASCADE)

    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f'{self.id} - {self.room}.'
    
from django.db import models
from django.contrib.auth.models import User

class Reservation(models.Model):
    ROOM_CHOICES = (
        ("1", "Basic"),
        ("2", "Premium"),
    )
    
    PAYMENT_CHOICES = (
        ('1', 'Pending'),
        ('2', 'Done'),
        ('3', 'Pay Later')
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.EmailField()
    phone_number = models.CharField(max_length=15)
    number_of_rooms = models.PositiveIntegerField()
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    room_numbers = models.CharField(max_length=255, help_text="Enter room numbers separated by commas")
    price = models.PositiveIntegerField()
    room_type = models.CharField(max_length = 1, default = "1", choices = ROOM_CHOICES)
    payment_status = models.CharField(max_length=1, default='1', choices = PAYMENT_CHOICES)

    def get_room_numbers(self):
        return self.room_numbers.split(',')

    def set_room_numbers(self, room_numbers):
        self.room_numbers = ','.join(room_numbers)

    room_numbers_list = property(get_room_numbers, set_room_numbers)


