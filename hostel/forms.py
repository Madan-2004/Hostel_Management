# forms.py
from django import forms
from .models import Reservation

class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'  # Use all fields from the Reservation model
        # If you want to exclude certain fields, use:
        # exclude = ['field1', 'field2', ...]
