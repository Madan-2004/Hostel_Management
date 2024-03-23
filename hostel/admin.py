from django.contrib import admin
from .models import Room, Booking, Reservation

# Register your models here.
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Reservation)
