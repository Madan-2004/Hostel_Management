from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="home"),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('stays/', views.stays, name="stays"),
    path('bookings/', views.bookings, name="bookings"),
    path('signup/', views.signup, name="signup"),
    path('book_room/', views.book_room, name='book_room')
]