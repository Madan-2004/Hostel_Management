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
    institute_use = models.BooleanField(default = False)
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
    id = models.AutoField(primary_key=True)
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

    def __str__(self):
        return f'{self.id}. {self.user.username} has booked {self.number_of_rooms} rooms.'

class Transaction(models.Model):
    txnid = models.CharField(primary_key = True, max_length = 20)
    reservation = models.ForeignKey(Reservation, on_delete=models.CASCADE, default=None)
    error_Message = models.TextField()
    net_amount_debit = models.DecimalField(max_digits=10, decimal_places=2)
    phone = models.CharField(max_length = 15)
    productinfo = models.CharField(max_length = 255)
    status = models.CharField(max_length = 10, default="failure")
    firstname = models.CharField(max_length = 64)
    lastname = models.CharField(max_length = 64)
    addedon = models.DateTimeField()
    encryptedPaymentId = models.CharField(max_length = 255)
    email = models.EmailField(default='all@iiti.ac.in')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payuMoneyId = models.CharField(max_length = 255)
    mihpayid = models.CharField(max_length = 255)

    def __str__(self):
        return f"{self.txnid} - {self.status}."
