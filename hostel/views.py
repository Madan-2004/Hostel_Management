from django.shortcuts import render ,redirect
from django.http import HttpResponse , HttpResponseRedirect
from .models import Room, Booking
# from .models import Hotels,Rooms,Reservation
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from hostel.booking_functions.availability import check_availability
from django.views.generic import ListView
from datetime import datetime, timedelta

class RoomList(ListView):
    model = Room

class BookingList(ListView):
    model = Booking

# Create your views here.
def index(request):
    return render(request, 'index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']

        user = authenticate(username = email, password = password)

        try:
            if user.is_staff:
                messages.warning(request, 'Incorrect username or password')
                return redirect('login')
        except:
            pass

        if user is not None:
            login(request,user)
            messages.success(request,"successful logged in")
            print("Login successfull")
            return redirect('/')
        
        else:
            messages.warning(request,"Incorrect username or password")
            return redirect('login')

    return render(request, 'login.html')

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

        for room in room_list:
            if check_availability(room, checkin_date, checkout_date):
                available_rooms.append(room)

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
        
        if len(available_rooms) >= capacity:
            return redirect('book_room')
        else:
            rem = capacity - len(available_rooms)
            return HttpResponse(f'{rem} rooms are not available.')

    return render(request, "stays.html")

def bookings(request):
    return render(request, "bookings.html")

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