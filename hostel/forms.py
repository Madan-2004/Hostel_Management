# forms.py
from django import forms
from .models import Reservation, Transaction

class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['txnid', 'net_amount_debit', 'phone', 'firstname', 'lastname', 'addedon', 'email', 'amount', 'payuMoneyId', 'mihpayid']
        
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = '__all__'  # Use all fields from the Reservation model
        # If you want to exclude certain fields, use:
        # exclude = ['field1', 'field2', ...]
