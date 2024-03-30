from django.contrib import admin
from .models import Room, Booking, Reservation, Transaction

# Register your models here.
admin.site.register(Room)
admin.site.register(Booking)
admin.site.register(Reservation)
admin.site.register(Transaction)
