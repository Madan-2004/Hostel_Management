from django.shortcuts import render ,redirect
from django.http import JsonResponse
from django.http import HttpResponse , HttpResponseRedirect, HttpResponseBadRequest
from .models import Room, Booking, Reservation, Transaction
from django.db.models import Count, Value
from django.db import models
# from .models import Hotels,Rooms,Reservation
from django.contrib import messages
from django.contrib.auth import authenticate,login as auth_login,logout as auth_logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from hostel.booking_functions.availability import check_availability
from django.views.generic import ListView
from datetime import datetime, timedelta
from django.shortcuts import redirect, get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.contrib.auth.decorators import login_required

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from paywix.payu import Payu
from django.conf import settings
import time, urllib

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from paywix.payu import Payu
from hashlib import sha512
# import uuid

# Retrieve the failure URL from settings

payu_config = settings.PAYU_CONFIG
merchant_key = payu_config.get('merchant_key')
merchant_salt = payu_config.get('merchant_salt')
furl = settings.PAYU_CONFIG.get('furl')
surl = settings.PAYU_CONFIG.get('surl')
mode = payu_config.get('mode')
payu = Payu(merchant_key, merchant_salt, mode)

class RoomList(ListView):
    model = Room

class BookingList(ListView):
    model = Booking

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username,password=password)

        if user is not None and user.is_active:
            auth_login(request,user)
            return render(request,'index.html')
        else:
            messages.error(request,'Invalid Credentials')
    return render(request, "login.html")  

@login_required(login_url='/login/')
def stays(request):
    if request.method == 'POST':
        check_in = request.POST.get('cin')
        check_out = request.POST.get('cout')
        capacity = int(request.POST.get('capacity'))
        category = request.POST.get('room_type')
        room_list = Room.objects.filter(category = category)
        available_rooms = []

        checkin_date = datetime.strptime(check_in, '%Y-%m-%d').date()
        checkout_date = datetime.strptime(check_out, '%Y-%m-%d').date()

        i = 0
        for room in room_list:
            if check_availability(room, checkin_date, checkout_date) and i < capacity and room.institute_use == False:
                available_rooms.append(room)
                i = i + 1

        available_room_nos = []
        for room in available_rooms:
            available_room_nos.append(room.room_no)

        request.session['stays_data'] = {
            'check_in': check_in,
            'check_out': check_out,
            'capacity': capacity,
            'category': category,
            'available_room_nos': available_room_nos
        }
        
        if len(available_rooms) == capacity:
            return redirect('book_room')
        else:
            rem = capacity - len(available_rooms)
            return redirect('not_available', rem)

    return render(request, "stays.html")

@login_required(login_url='/login/')
def not_available(request, rem):
    return render(request, "not_available.html", {'rem': rem})


@login_required(login_url='/login/')
def bookings(request):
    user_reservations = Reservation.objects.filter(user=request.user)

    return render(request, "bookings.html", {'user_reservations': user_reservations})

def signup(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 != password2:
            messages.warning(request, "Password mismatch! Please try again.")
            return redirect('login')
        
        try: 
            if User.objects.filter(username=email).exists():
                messages.warning(request, "Email already exists!")
                return redirect('login')

        
        except:
            pass

        new_user = User.objects.create_user(username=email, password=password1)
        new_user.is_superuser=False
        new_user.is_staff=False
        new_user.save()
        messages.success(request,"Registration Successfull")
        return redirect("login")
    return HttpResponse('Access Denied')

def book_room(request):
    stays_data = request.session.get('stays_data')
    user_name = None
    if request.user.is_authenticated:
        user_name = request.user

    if request.method == 'POST':
        email = request.POST['email']
        phoneno = request.POST['phoneno']
        check_in = stays_data['check_in']
        check_out = stays_data['check_out']
        capacity = stays_data['capacity']
        category = stays_data['category']
        available_room_nos = stays_data['available_room_nos']
        amount=0
        user = User.objects.get(username=user_name.username)
        length_of_stay = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        for r in available_room_nos:
            room_info = Room.objects.get(room_no = r)
            amount=amount+(length_of_stay * int(room_info.rent))
            new_booking = Booking.objects.create(
                user = user_name,
                phone_number = phoneno,
                email = email,
                room = room_info,
                check_in = check_in,
                check_out = check_out
            )

            new_booking.save()

        reservation = Reservation.objects.create(
            user=user_name,
            email=email,
            phone_number=phoneno,
            number_of_rooms=len(available_room_nos),
            check_in_date=check_in,
            check_out_date=check_out,
            room_numbers_list=available_room_nos,
            price=amount,
            room_type=category
        )

        reservation.save()

        return redirect('bookings')

    if not stays_data:
        # Handle case where session data is not available
        return HttpResponse("Session data not found.")

    check_in = stays_data['check_in']
    check_out = stays_data['check_out']
    capacity = stays_data['capacity']
    category = stays_data['category']
    available_room_nos = stays_data['available_room_nos']


    return render(request, 'book_room.html', {
        'check_in': check_in,
        'check_out': check_out,
        'capacity': capacity,
        'category': category,
        'available_room_nos': available_room_nos
    })


def delete_booking(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Retrieve room numbers associated with the reservation
    room_numbers = reservation.room_numbers_list

    # Delete bookings associated with these room numbers and within the check-in and check-out dates
    Booking.objects.filter(room__room_no__in=room_numbers, 
                            check_in__gte=reservation.check_in_date, 
                            check_out__lte=reservation.check_out_date).delete()

    reservation.delete()

    return redirect('bookings')

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return render(request,'index.html') 

@login_required
def pay_now(request, reservation_id):
    # Set the API endpoint URL
    reservation = Reservation.objects.get(id = reservation_id)
    apiEndpoint = "https://secure.payu.in/_payment"

    # Set the merchant key and salt
    merchantKey = settings.PAYU_CONFIG.get('merchant_key')
    salt = settings.PAYU_CONFIG.get('merchant_salt')

    # Set the order details
    amount = reservation.price
    productInfo = "IIT Indore"
    firstName = reservation.user.username
    email = reservation.email
    phone = reservation.phone_number
    txnId = str(int(time.time())) 
    surl = f"http://127.0.0.1:8000/payment_response/?reservation_id={reservation_id}"
    furl = f"http://127.0.0.1:8000/payment_response/?reservation_id={reservation_id}"

    # Create a map of parameters to pass to the PayU API
    params = {
        "key": merchantKey,
        "txnid": txnId,
        "amount": amount,
        "productinfo": productInfo,
        "firstname": firstName,
        "email": email,
        "phone": phone,
        "surl": surl,
        "furl": furl
    }

    # Generate the hash
    hashValue = generateHash(params, salt)

    # Add the hash to the parameter map
    params["hash"] = hashValue

    # Encode the parameters for use in the URL
    encodedParams = urllib.parse.urlencode(params)

    # Build the URL for the PayU API request
    url = apiEndpoint + "?" + encodedParams

    # Output the URL for the PayU API request
    print(url)
    return render(request, "payment_form.html", params)

def generateHash(params, salt):
    hashString = params["key"] + "|" + params["txnid"] + "|" + str(params["amount"]) + "|" + params["productinfo"] + "|" + params['firstname'] + "|" + params['email'] + "|" +"|" +"|" +"|" +"|" +"|" + "|" +"|" +"|" +"|" + "|" + salt
    return sha512(hashString.encode('utf-8')).hexdigest()

@csrf_exempt
def payment_response(request):
    if request.method == "POST":
        response = JsonResponse(dict(request.POST.items()))
        reservation_id = request.GET.get('reservation_id')
        reservation = get_object_or_404(Reservation, id=reservation_id)
        new_payment_response = Transaction.objects.create(
            txnid = request.POST.get('txnid'),
            reservation = reservation,
            error_Message = request.POST.get('error_Message'),
            net_amount_debit = request.POST.get('net_amount_debit'),
            phone = request.POST.get('phone'),
            productinfo = request.POST.get('productinfo'),
            status = request.POST.get('status'),
            firstname = request.POST.get('firstname'),
            lastname = request.POST.get('lastname'),
            addedon =  request.POST.get('addedon'),
            encryptedPaymentId = request.POST.get('encryptedPaymentId'),
            email = request.POST.get('email'),
            amount = request.POST.get('amount'),
            payuMoneyId = request.POST.get('payuMoneyId'),
            mihpayid = request.POST.get('mihpayid')
        )
        new_payment_response.save()

        if request.POST.get('status') == "success":
            # Redirect to payment success page
            return redirect('payment_success', txnid=request.POST.get('txnid'))
        elif request.POST.get('status') == "failure":
            # Redirect to payment failure page
            return redirect('payment_failure', txnid=request.POST.get('txnid'))
        else:
            # Handle other statuses if needed
            return HttpResponseBadRequest("Invalid payment status")
    else:
        return HttpResponseBadRequest("Invalid request method")

def payment_success(request, txnid):
    if request.method == "POST":
        reservation_id = request.GET.get('reservation_id')
        txnid = request.GET.get('txnid')

        # Retrieve reservation object using reservation_id
        try:
            reservation = Reservation.objects.get(id=reservation_id)
        except Reservation.DoesNotExist:
            return HttpResponseBadRequest("Invalid reservation ID")

        # Pass reservation_id and txnid to the template
        return render(request, 'payment_success.html', {'txnid': txnid})

    return HttpResponseBadRequest("Method not allowed")

def payment_failure(request, txnid):
    return render(request, 'payment_failure.html', {'txnid': txnid})