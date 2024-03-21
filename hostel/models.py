from django.db import models
from django.core.validators import MinValueValidator
from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.conf import settings
# Create your models here.
# class Hotels(models.Model):
#     #h_id,h_name,owner ,location,rooms
#     name = models.CharField(max_length=30,default="101A", unique = True)
#     # owner = models.CharField(max_length=20)
#     location = models.CharField(max_length=50, default = "IIT Indore")
#     state = models.CharField(max_length=50,default="Indore")
#     country = models.CharField(max_length=50,default="India")
#     def __str__(self):
#         return self.name


# class Rooms(models.Model):
#     ROOM_STATUS = ( 
#     ("1", "available"), 
#     ("2", "not available"),    
#     ) 

#     ROOM_TYPE = ( 
#     ("1", "premium"), 
#     ("2", "deluxe")
#     # ("3","basic"),    
#     ) 

#     #type,no_of_rooms,capacity,prices,Hotel
#     room_type = models.CharField(max_length=50,choices = ROOM_TYPE)
#     capacity = models.IntegerField()
#     price = models.IntegerField()
#     size = models.IntegerField()
#     # hotel = models.ForeignKey(Hotels, on_delete = models.CASCADE)
#     status = models.CharField(choices =ROOM_STATUS,max_length = 15)
#     roomnumber = models.ForeignKey(Hotels, on_delete= models.CASCADE)
#     def __str__(self):
#         return self.hotel.name

# class Reservation(models.Model):

#     check_in = models.DateField(auto_now =False)
#     check_out = models.DateField()
#     room = models.ForeignKey(Rooms, on_delete = models.CASCADE)
#     guest = models.ForeignKey(User, on_delete= models.CASCADE)
    
#     booking_id = models.CharField(max_length=100,default="null")
#     def __str__(self):
#         return self.guest.username

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

    room = models.ForeignKey(Room, on_delete = models.CASCADE)

    check_in = models.DateField()
    check_out = models.DateField()

    def __str__(self):
        return f'{self.user} has booked {self.room}.'
    


