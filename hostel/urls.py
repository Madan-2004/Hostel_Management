from django.urls import path
from . import views
from .views import delete_booking

urlpatterns = [
    path('', views.index, name="home"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('stays/', views.stays, name="stays"),
    path('bookings/', views.bookings, name="bookings"),
    path('signup/', views.signup, name="signup"),
    path('book_room/', views.book_room, name='book_room'),
    path('not_available/<int:rem>/', views.not_available, name='not_available'),
    path('delete-booking/<int:reservation_id>/', delete_booking, name='delete_booking'),
    path('pay_now/<int:reservation_id>/', views.pay_now, name='pay_now'),
    path('payment_response/', views.payment_response, name='payment_response'),
    path('payment_success/<str:txnid>/', views.payment_success, name='payment_success'),
    path('payment_failure/<str:txnid>/', views.payment_failure, name='payment_failure'),
    path('download-invoice/<int:reservation_id>/', views.generate_invoice_pdf, name='download_invoice'),

    path('admin_login/', views.admin_login, name='admin_login'),
    path('admin_index/', views.admin_index, name='admin_index'),
    path('admin_requests/', views.admin_requests, name='admin_requests'),
    path('view_reservation/<int:reservation_id>/', views.view_reservation, name='view_reservation'),
    path('edit_reservation/<int:reservation_id>/', views.edit_reservation, name='edit_reservation'),
]