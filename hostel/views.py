from django.shortcuts import render ,redirect
from django.http import JsonResponse
from django.http import HttpResponse , HttpResponseRedirect
from .models import Room, Booking, Reservation
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

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from paywix.payu import Payu
from hashlib import sha512
import uuid

# Retrieve the failure URL from settings

payu_config = settings.PAYU_CONFIG
merchant_key = payu_config.get('merchant_key')
merchant_salt = payu_config.get('merchant_salt')
furl = settings.PAYU_CONFIG.get('furl')
surl = settings.PAYU_CONFIG.get('surl')
mode = payu_config.get('mode')
payu = Payu(merchant_key, merchant_salt, mode)

@csrf_exempt
def payu_demo(request):
    if request.method == 'GET':
        data = {
            'amount': '10',
            'firstname': 'rishikesh',
            'email': 'rishidevkate@gmail.com',
            'phone': '7276034203',
            'productinfo': 'test',
            'lastname': 'test',
            'address1': 'test',
            'address2': 'test',
            'city': 'test',
            'state': 'test',
            'country': 'test',
            'zipcode': 'tes',
            'surl': surl,
            'furl': furl
        }
        data.update({"txnid": "123456789"})

        # Generate hash
        hash_string = merchant_key + '|' + data['txnid'] + '|' + data['amount'] + '|' + data['productinfo'] + '|' + data['firstname'] + '|' + data['email'] + '|||||||||||' + merchant_salt
        # hash_value = sha512(hash_string.encode('utf-8')).hexdigest()
        hash_value = uuid.uuid4()

        # Include hash in transaction data
        data['hash'] = hash_value

        # Initiate transaction
        payu_data = payu.transaction(**data)
        return render(request, 'payu_checkout.html', {"posted": payu_data})
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
@csrf_exempt
def payu_success(request):
    if request.method == 'POST':
        data = {k: v[0] for k, v in dict(request.POST).items()}
        response = payu.verify_transaction(data)
        return JsonResponse(response)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)
    
@csrf_exempt
def payu_failure(request):
    if request.method == 'POST':
        data = {k: v[0] for k, v in dict(request.POST).items()}
        response = payu.verify_transaction(data)
        return JsonResponse(response)
    else:
        return JsonResponse({"error": "Method not allowed"}, status=405)


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
            if check_availability(room, checkin_date, checkout_date) and i < capacity:
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

        return redirect('payu_demo')

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