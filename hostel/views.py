from django.shortcuts import render ,redirect
from django.http import JsonResponse
from django.http import HttpResponse , HttpResponseRedirect, HttpResponseBadRequest
from .models import Room, Booking, Reservation, Transaction
from allauth.socialaccount.models import SocialAccount

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
from django.core.exceptions import ObjectDoesNotExist

from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.conf import settings
import time, urllib

from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from hashlib import sha512
from django.contrib.auth.models import User

# Retrieve the failure URL from settings

payu_config = settings.PAYU_CONFIG
merchant_key = payu_config.get('merchant_key')
merchant_salt = payu_config.get('merchant_salt')
furl = settings.PAYU_CONFIG.get('furl')
surl = settings.PAYU_CONFIG.get('surl')
mode = payu_config.get('mode')

class RoomList(ListView):
    model = Room

class BookingList(ListView):
    model = Booking

# Create your views here.
def index(request):
    if request.user.is_authenticated:
        try:
            social_account = SocialAccount.objects.get(user=request.user)
            extra_data = social_account.extra_data
            
            # Extract username and email from extra_data
            username = extra_data.get('name', '')
            email = extra_data.get('email', '')
            
            # You can process or display the username and email as needed
            context = {
                'username': username,
                'email': email,
            }
            return render(request, 'index.html', context)
        
        except SocialAccount.DoesNotExist:
            # Handle the case when the user doesn't have a social account
            # For example, you can use the user's username and email from the default Django user model
            username = request.user.username
            email = request.user.email
            context = {
                'username': username,
                'email': email,
            }
            return render(request, 'index.html', context)
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
        category = request.POST.get('category')
        room_list = Room.objects.all()
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
    email = None
    try:
        email = SocialAccount.objects.get(user=request.user).extra_data.get('email', '')
    except:
        social_account = None
    user_reservations = Reservation.objects.filter(email = email)
    project_reservations = Reservation.objects.filter(project_email = email,  verified_status = '1')

    return render(request, 'bookings.html', {'user_reservations': user_reservations, 'project_reservations': project_reservations})

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
    user_name = request.user
    email = None

    if request.user.is_authenticated:
        social_account = SocialAccount.objects.get(user=request.user)
        extra_data = social_account.extra_data
            
        # Extract username and email from extra_data
        name = extra_data.get('name', '')
        email = extra_data.get('email', '')

    if request.method == 'POST':
        email = SocialAccount.objects.get(user=request.user).extra_data.get('email', '')
        phoneno = request.POST['phoneno']
        check_in = stays_data['check_in']
        check_out = stays_data['check_out']
        capacity = stays_data['capacity']
        category = stays_data['category']
        available_room_nos = stays_data['available_room_nos']
        payment_method = request.POST.get('payment_method')
        project_email = request.POST.get('project_email', '')
        project_description = request.POST.get('project_description', '')
        amount=0.0
        room_rent = 0
        if category == '1':
            room_rent = 300
        elif category == '2':
            room_rent = 350
        else:
            room_rent = 400
        tariff_per_day = room_rent
        user = User.objects.get(username=user_name.username)
        length_of_stay = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
        for r in available_room_nos:
            amount += length_of_stay * int(room_rent)

        total_price = int(amount) + (0.12*int(amount))

        reservation = Reservation.objects.create(
            user=user_name,
            email=email,
            phone_number=phoneno,
            payment_method=payment_method,
            number_of_rooms=len(available_room_nos),
            check_in_date=check_in,
            check_out_date=check_out,
            room_numbers_list=available_room_nos,
            price = amount,   
            total_price = total_price,
            length_of_stay = length_of_stay,
            tariff_per_day = tariff_per_day,
            gst = float(amount)*0.12
        )

        if payment_method == '2' and project_email:
            reservation.project_email = project_email
            reservation.project_description = project_description
            reservation.save()

        reservation.save()

        for r in available_room_nos:
            room_info = Room.objects.get(room_no = r)
            new_booking = Booking.objects.create(
                user = user_name,
                phone_number = phoneno,
                email = email,
                room = room_info,
                check_in = check_in,
                check_out = check_out,
                reservation = reservation
            )

            new_booking.save()

        return redirect('bookings')

    if not stays_data:
        # Handle case where session data is not available
        return HttpResponse("Session data not found.")

    check_in = stays_data['check_in']
    check_out = stays_data['check_out']
    capacity = stays_data['capacity']
    category = stays_data['category']
    available_room_nos = stays_data['available_room_nos']

    amount=0.0
    room_rent = 0
    if category == '1':
        room_rent = 300
    elif category == '2':
        room_rent = 350
    else:
        room_rent = 400

    length_of_stay = (datetime.strptime(check_out, "%Y-%m-%d") - datetime.strptime(check_in, "%Y-%m-%d")).days
    for r in available_room_nos:
        amount += length_of_stay * int(room_rent)

    return render(request, 'book_room.html', {
        'check_in': check_in,
        'check_out': check_out,
        'capacity': capacity,
        'price': int(amount)+(int(amount)*0.12), #GST.
        'available_room_nos': available_room_nos,
        'email': email,
        'name': name
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
    amount = reservation.total_price
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
        "amount": 1,
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
            reservation.payment_status = '2'  # '2' represents 'Done' in PAYMENT_CHOICES
            reservation.save()
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
    transaction = get_object_or_404(Transaction, txnid=txnid)
    reservation_id = transaction.reservation.id
    
    send_invoice_email(transaction)

    return render(request, 'payment_success.html', {'txnid': txnid, 'reservation_id': reservation_id})


def payment_failure(request, txnid):
    transaction = get_object_or_404(Transaction, txnid=txnid)
    reservation = transaction.reservation
    number_of_rooms = reservation.number_of_rooms
    addedon =  transaction.addedon
    amount = transaction.amount
    error_Message = transaction.error_Message
    return render(request, 'payment_failure.html', {'txnid': txnid, 'addedon': addedon, 'amount': amount, 'error_Message': error_Message, 'number_of_rooms': number_of_rooms})

from django.template.loader import get_template
from django.conf import settings
from xhtml2pdf import pisa

def generate_invoice_pdf(request, reservation_id):
    # Retrieve transaction details
    reservation = get_object_or_404(Reservation, id=reservation_id)

    # Retrieve transaction associated with the reservation
    try:
        transaction = get_object_or_404(Transaction, reservation=reservation, status = "success")
        txnid = transaction.txnid
    except Transaction.DoesNotExist:
        # Handle the case where no transaction is found for the reservation
        return HttpResponseBadRequest("No transaction found for this reservation")

    # Render invoice HTML template with transaction details
    template_path = 'invoice.html'
    context = {'transaction': transaction, 'reservation': reservation}
    template = get_template(template_path)
    html = template.render(context)

    # Create PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="invoice_{txnid}.pdf"'
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse('We had some errors <pre>' + html + '</pre>')
    return response


from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags

def send_invoice_email(transaction):
    subject = 'Invoice for Your Purchase'
    from_email = settings.EMAIL_HOST_USER
    to_email = transaction.email
    reservation = transaction.reservation

    # Render HTML content from template
    html_content = render_to_string('invoice.html', {'transaction': transaction, 'reservation': reservation})

    # Create a text/plain version of the HTML email (for clients that do not support HTML emails)
    text_content = strip_tags(html_content)

    # Create EmailMultiAlternatives object to include both HTML and text content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    # Send email
    msg.send()



# Admin Login
from django.contrib.auth.decorators import login_required
from .decorators import admin_required
admin_users = settings.ALLOWED_ADMIN_USERNAMES

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request,username=username,password=password)

        if user is not None and user.is_active:
            auth_login(request,user)
            return redirect('admin_requests')
        else:
            messages.error(request,'Invalid Credentials')
    return render(request, "admin/admin_login.html")

@login_required(login_url='/login/')
@admin_required(admin_users)
def admin_index(request):
    reservations = Reservation.objects.all()

    return render(request, 'admin/admin_index.html', {'reservations': reservations})

@login_required(login_url='/login/')
@admin_required(admin_users)
def admin_requests(request):
    if request.method == 'POST':
        action = request.POST.get('action')
        reservation_id = request.POST.get('reservation_id')
        reservation = Reservation.objects.get(id=reservation_id)

        if action == 'accept':
            reservation.verified_status = '1'  # Assuming '1' represents 'Accepted'
            reservation.save()
            send_booking_confirmation_email(reservation)
            # Check if payment method is through project
            payment_method = reservation.payment_method
            if payment_method == '2':
                send_project_payment_email(reservation)

        elif action == 'reject':
            delete_booking(request, reservation_id)
            send_booking_rejection_email(reservation)

        else:
            return HttpResponseBadRequest("Invalid action")
    unverified_reservations = Reservation.objects.filter(verified_status='3')
    quantity = len(unverified_reservations)
    
    return render(request, 'admin/admin_requests.html', {'quantity': quantity, 'unverified_reservations': unverified_reservations})


from django.utils import timezone
@login_required(login_url='/login/')
@admin_required(admin_users)
def availability(request):
    # Get today's date
    today = timezone.now().date()
    
    # Retrieve bookings for the next 30 days
    end_date = today + timedelta(days=30)
    bookings_check_in = Booking.objects.filter(check_in__range=[today, end_date], reservation__verified_status='1')
    bookings_check_out = Booking.objects.filter(check_out__range=[today, end_date], reservation__verified_status='1')

    # Combine the two querysets using the | operator
    bookings = bookings_check_in | bookings_check_out
    
    # Create a dictionary to store availability data for each day
    availability_data = {}
    
    # Iterate over each day between today and the end date
    current_date = today
    while current_date <= end_date:
        # Count the number of bookings for the current day
        bookings_on_date = bookings.filter(check_in__lte=current_date, check_out__gte=current_date).count()
        
        # Calculate the number of available rooms
        total_rooms = Room.objects.count()
        available_rooms = total_rooms - bookings_on_date
        
        # Store availability data for the current day in the dictionary
        availability_data[current_date] = {
            'bookings': bookings_on_date,
            'available_rooms': available_rooms
        }
        
        # Move to the next day
        current_date += timedelta(days=1)
    
    # Render the availability template with availability data
    return render(request, 'admin/availability.html', {'availability_data': availability_data})

@login_required
@admin_required(admin_users)
def view_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    if request.method == 'POST':
        action = request.POST.get('action')
        reservation_id = request.POST.get('reservation_id')
        reservation = Reservation.objects.get(id=reservation_id)

        if action == 'accept':
            reservation.verified_status = '1'  # Assuming '1' represents 'Accepted'
            reservation.save()
            send_booking_confirmation_email(reservation)
            # Check if payment method is through project
            payment_method = reservation.payment_method
            if payment_method == '2':
                send_project_payment_email(reservation)
                return redirect('admin_index')

        elif action == 'reject':
            delete_booking(request, reservation_id)
            send_booking_rejection_email(reservation)
            return redirect('admin_index')

        else:
            return HttpResponseBadRequest("Invalid action")
    return render(request, 'admin/view_reservation.html', {'reservation': reservation})

from .forms import ReservationForm, TransactionForm

import copy
from django.db import transaction as db_transaction

@login_required
@admin_required(admin_users)
def edit_reservation(request, reservation_id):
    initial_reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation = copy.deepcopy(initial_reservation) 
    if request.method == 'POST':
        form = ReservationForm(request.POST, instance=initial_reservation)
        if form.is_valid():
            new_reservation = form.save(commit=False)

            # Check if room numbers have changed
            if reservation.room_numbers != new_reservation.room_numbers:
                with db_transaction.atomic():
                    # Delete existing bookings associated with the old room numbers
                    old_room_numbers = reservation.room_numbers_list
                    for room_number in old_room_numbers:
                        bookings_to_delete = Booking.objects.filter(
                            room__room_no=room_number,
                            reservation = reservation
                        )
                        bookings_to_delete.delete()

                    # Create new bookings for the new room numbers
                    new_room_numbers = new_reservation.room_numbers_list
                    for room_number in new_room_numbers:
                        new_booking = Booking.objects.create(
                            user=new_reservation.user,
                            phone_number=new_reservation.phone_number,
                            email=new_reservation.email,
                            room=Room.objects.get(room_no=room_number),
                            check_in=new_reservation.check_in_date,
                            check_out=new_reservation.check_out_date,
                            reservation = reservation
                        )
                        new_booking.save()
                    
                    new_reservation.number_of_rooms = len(new_room_numbers)
                    new_reservation.room_numbers = ','.join(new_room_numbers)
                    new_reservation.length_of_stay = (new_reservation.check_out_date - new_reservation.check_in_date).days
                    tariff_per_day = new_reservation.tariff_per_day
                    length_of_stay = new_reservation.length_of_stay
                    cost = (new_reservation.length_of_stay * new_reservation.number_of_rooms)*tariff_per_day
                    gst = float(cost)*0.12
                    new_reservation.price = cost
                    new_reservation.gst = gst
                    new_reservation.total_price = float(cost)+gst

            if reservation.number_of_rooms != new_reservation.number_of_rooms:
                with db_transaction.atomic():
                    # Calculate the difference in the number of rooms
                    diff_rooms = new_reservation.number_of_rooms - reservation.number_of_rooms

                    if diff_rooms > 0:  # Add new rooms
                        available_rooms = []
                        room_list = Room.objects.all()
                        checkin_date = new_reservation.check_in_date
                        checkout_date = new_reservation.check_out_date

                        # Find available rooms for booking
                        for room in room_list:
                            if check_availability(room, checkin_date, checkout_date) and len(available_rooms) < diff_rooms and not room.institute_use:
                                available_rooms.append(room)

                        if len(available_rooms) == diff_rooms:
                            # Make bookings for the new rooms
                            for room in available_rooms:
                                new_booking = Booking.objects.create(
                                    user=new_reservation.user,
                                    phone_number=new_reservation.phone_number,
                                    email=new_reservation.email,
                                    room=room,
                                    check_in=new_reservation.check_in_date,
                                    check_out=new_reservation.check_out_date,
                                    reservation=reservation
                                )
                                
                            # Update reservation details
                            new_reservation.room_numbers_list = [booking.room.room_no for booking in Booking.objects.filter(reservation=reservation)]
                            new_reservation.room_numbers_list = new_reservation.get_room_numbers()                
                            new_reservation.length_of_stay = (new_reservation.check_out_date - new_reservation.check_in_date).days
                            tariff_per_day = new_reservation.tariff_per_day
                            length_of_stay = new_reservation.length_of_stay
                            cost = (length_of_stay * new_reservation.number_of_rooms) * tariff_per_day
                            gst = float(cost) * 0.12
                            new_reservation.price = cost
                            new_reservation.gst = gst
                            new_reservation.total_price = float(cost) + gst  

                    elif diff_rooms < 0:  # Delete existing rooms
                        with db_transaction.atomic():
                            rooms_to_delete = reservation.room_numbers_list[diff_rooms:]
                            for room_number in rooms_to_delete:
                                booking_to_delete = Booking.objects.filter(room__room_no=room_number, reservation=reservation)
                                booking_to_delete.delete()

                        # Update reservation details
                        new_reservation.room_numbers_list = [booking.room.room_no for booking in Booking.objects.filter(reservation=reservation)]
                        new_reservation.room_numbers_list = new_reservation.get_room_numbers()                
                        new_reservation.length_of_stay = (new_reservation.check_out_date - new_reservation.check_in_date).days
                        tariff_per_day = new_reservation.tariff_per_day
                        length_of_stay = new_reservation.length_of_stay
                        cost = (length_of_stay * new_reservation.number_of_rooms) * tariff_per_day
                        gst = float(cost) * 0.12
                        new_reservation.price = cost
                        new_reservation.gst = gst
                        new_reservation.total_price = float(cost) + gst                

            # Check if check-in date has changed
            if reservation.check_in_date != new_reservation.check_in_date:
                with db_transaction.atomic():
                    room_numbers = reservation.room_numbers_list
                    for room_no in room_numbers:
                        room_details = Room.objects.get(room_no=room_no)
                        bookings_to_update = Booking.objects.filter(room=room_details, reservation = reservation)
                        for booking in bookings_to_update:
                            booking.check_in = new_reservation.check_in_date
                            booking.save()
                new_reservation.length_of_stay = (new_reservation.check_out_date - new_reservation.check_in_date).days
                tariff_per_day = new_reservation.tariff_per_day
                length_of_stay = new_reservation.length_of_stay
                cost = (length_of_stay*new_reservation.number_of_rooms)*tariff_per_day
                gst = float(cost)*0.12
                new_reservation.price = cost
                new_reservation.gst = gst
                new_reservation.total_price = float(cost)+gst

            # Check if check-out date has changed
            if reservation.check_out_date != new_reservation.check_out_date:
                with db_transaction.atomic():
                    room_numbers = reservation.room_numbers_list
                    for room_no in room_numbers:
                        room_details = Room.objects.get(room_no=room_no)
                        bookings_to_update = Booking.objects.filter(room=room_details, reservation = reservation)
                        for booking in bookings_to_update:
                            booking.check_out = new_reservation.check_out_date
                            booking.save()
                new_reservation.length_of_stay = (new_reservation.check_out_date - new_reservation.check_in_date).days
                tariff_per_day = new_reservation.tariff_per_day
                length_of_stay = new_reservation.length_of_stay
                cost = (length_of_stay*new_reservation.number_of_rooms)*tariff_per_day
                gst = float(cost)*0.12
                new_reservation.price = cost
                new_reservation.gst = gst
                new_reservation.total_price = float(cost)+gst
                    
            new_reservation.save()
            return redirect('admin_index')  # Redirect to the admin home page
    else:
        form = ReservationForm(instance=reservation)
    return render(request, 'admin/edit_reservation.html', {'form': form, 'reservation': reservation})


def send_project_payment_email(reservation):
    subject = 'Confirmation for room bookings'
    from_email = settings.EMAIL_HOST_USER
    to_email = reservation.project_email

    # Render HTML content from template
    html_content = render_to_string('email/project_payment_confirmation.html', {'reservation': reservation})

    # Create a text/plain version of the HTML email (for clients that do not support HTML emails)
    text_content = strip_tags(html_content)

    # Create EmailMultiAlternatives object to include both HTML and text content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    # Send email
    msg.send()

def accept_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    reservation.payment_status = '3'  # Update payment status
    reservation.save()
    # Send acceptance email
    send_reservation_email(reservation, 'Reservation Accepted', 'email/project_acceptance_email.html')
    return redirect('bookings')

def reject_reservation(request, reservation_id):
    reservation = Reservation.objects.get(id=reservation_id)
    # Send rejection email
    send_reservation_email(reservation, 'Reservation Rejected', 'email/project_rejection_email.html')
    delete_booking(request, reservation_id) # Delete the reservation
    return redirect('bookings')


def send_booking_confirmation_email(reservation):
    subject = 'Booking Request Confirmation'
    from_email = settings.EMAIL_HOST_USER
    to_email = reservation.email

    # Render HTML content from template
    html_content = render_to_string('email/booking_confirmation_email.html', {'reservation': reservation})

    # Create a text/plain version of the HTML email (for clients that do not support HTML emails)
    text_content = strip_tags(html_content)

    # Create EmailMultiAlternatives object to include both HTML and text content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(text_content, "text/plain")  # Attach plain text version of the email

    # Send email
    msg.send()

def send_booking_rejection_email(reservation):
    subject = 'Booking Request Rejection'
    from_email = settings.EMAIL_HOST_USER
    to_email = reservation.email

    # Render HTML content from template
    html_content = render_to_string('email/booking_rejection_email.html', {'reservation': reservation})

    # Create a text/plain version of the HTML email (for clients that do not support HTML emails)
    text_content = strip_tags(html_content)

    # Create EmailMultiAlternatives object to include both HTML and text content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(text_content, "text/plain")  # Attach plain text version of the email

    # Send email
    msg.send()

def send_reservation_email(reservation, subject, template):
    from_email = settings.EMAIL_HOST_USER
    to_email = reservation.email

    # Render HTML content from template
    html_content = render_to_string(template, {'reservation': reservation})

    # Create a text/plain version of the HTML email (for clients that do not support HTML emails)
    text_content = strip_tags(html_content)

    # Create EmailMultiAlternatives object to include both HTML and text content
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to_email])
    msg.attach_alternative(html_content, "text/html")

    # Send email
    msg.send()

