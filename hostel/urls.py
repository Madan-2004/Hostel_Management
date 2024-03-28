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
    path('pay_now/<int:reservation_id>/', views.pay_now, name='pay_now')
]